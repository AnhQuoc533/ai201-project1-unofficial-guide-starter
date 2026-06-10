"""Ingestion and chunking layers for The Unofficial Guide RAG pipeline.

This module implements the first two stages of the pipeline (see planning.md
Architecture):

    DOCUMENT INGESTION  ->  CHUNKING

  * ingest_documents()  collects raw text from each source using a loader
                        appropriate to its type (Google Docs export URL,
                        BeautifulSoup for ordinary HTML pages). Sources that
                        can't be scraped (blocked hosts or JS-only pages) are
                        read straight from a stored PDF/snapshot copy. Returns a
                        list of dicts with metadata:
                        {text, source, url, title, doc_type, date}.

  * chunk_documents()   splits each document's text with LangChain's
                        RecursiveCharacterTextSplitter, length-measured by the
                        all-MiniLM-L6-v2 tokenizer, into token-bounded chunks
                        with overlap. Each chunk keeps the parent metadata and
                        gains one extra field: chunk_id.

All tunable values come from config.py.
"""

import os
import re
import sys

# Silence the transformers "None of PyTorch, TensorFlow, or Flax have been
# found" advisory: this pipeline uses only the tokenizer (no model backend)
# until embedding in Milestone 4.
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

import config

# =========================================================================== #
# Cleaning
# =========================================================================== #

_BOILERPLATE_RE = re.compile("|".join(config.BOILERPLATE_PATTERNS), re.IGNORECASE)
_INLINE_LINK_RE = re.compile(config.INLINE_LINK_PATTERN)
_ARTIFACT_RE = re.compile(config.ARTIFACT_PATTERN)


def clean_text(raw):
    """Normalize whitespace and strip navigation / boilerplate / icon cruft.

    Ensures no leftover "Skip to main content", cookie banners, menu items, link
    fragments, or misrendered icon glyphs reach the chunks we ship downstream.
    """
    # Remove parenthesized relative-link references first, on the whole text:
    # PDF extraction often splits one link across two lines ("(/events?\n
    # topic_tags=..&show=upcoming)"), which a per-line pass would miss.
    raw = _INLINE_LINK_RE.sub(" ", raw)

    lines = []
    prev = None
    for line in raw.splitlines():
        line = _ARTIFACT_RE.sub("", line)
        line = re.sub(r"[ \t\xa0]+", " ", line).strip()
        if not line:
            continue
        if _BOILERPLATE_RE.search(line):
            continue
        # Drop consecutive duplicate lines (repeated nav items, etc.).
        if line == prev:
            continue
        lines.append(line)
        prev = line

    text = "\n".join(lines)
    # Collapse 3+ blank lines into a single paragraph break.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# =========================================================================== #
# Per-source-type loaders
# =========================================================================== #

def load_gdoc(url):
    """Load a shared Google Doc via its plain-text export endpoint.

    A normal doc URL renders as a JavaScript app; the /export?format=txt
    endpoint returns the document body as plain text, which needs no scraping.
    """
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError(f"Could not extract Google Doc id from {url!r}")
    doc_id = match.group(1)
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    resp = requests.get(export_url, headers=config.HEADERS,
                        timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def load_html(url):
    """Load an ordinary HTML page and extract its main textual content.

    Uses BeautifulSoup (lxml parser): strips boilerplate tags, narrows to the
    main content container when one is identifiable, then emits text with line
    breaks preserved so the cleaner and splitter have structure to work with.
    """
    resp = requests.get(url, headers=config.HEADERS,
                        timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding or "utf-8"

    soup = BeautifulSoup(resp.text, "lxml")

    for tag in soup(config.STRIP_TAGS):
        tag.decompose()

    container = None
    for selector in config.CONTENT_SELECTORS:
        found = soup.select_one(selector)
        # Require a container with real text, not an empty SPA mount point.
        if found and len(found.get_text(strip=True)) > 200:
            container = found
            break
    if container is None:
        container = soup.body or soup

    return container.get_text(separator="\n")


def load_pdf(filename):
    """Extract text from a user-saved PDF in documents/pdf/.

    Used for sources that can't be scraped live (JS single-page apps, or hosts
    that block non-browser traffic): the user prints the page to PDF and drops
    it here. pdfplumber extracts the text layer page by page.
    """
    import pdfplumber  # lazy import: only needed when a PDF fallback is used

    path = config.PDF_DIR / filename
    if not path.exists():
        raise FileNotFoundError(path)
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages)


def load_snapshot(filename):
    """Read a hand-saved .txt copy of a source from documents/snapshots/."""
    path = config.SNAPSHOT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


LOADERS = {
    "gdoc": load_gdoc,
    "html": load_html,
}


def _looks_unusable(text):
    """True if cleaned text is too short or looks like a block/SPA shell page."""
    if len(text) < config.MIN_USABLE_CHARS:
        return True
    low = text.lower()
    return any(marker in low for marker in config.UNUSABLE_MARKERS)


def _load_local(spec):
    """Return (clean_text, origin) from a user-saved PDF or .txt snapshot,
    trying the PDF first. ("", "") if neither yields non-empty content.
    User-provided copies are trusted, so only emptiness disqualifies them.
    """
    for kind, loader_fn in (("pdf", load_pdf), ("snapshot", load_snapshot)):
        name = spec.get(kind)
        if not name:
            continue
        try:
            candidate = clean_text(loader_fn(name))
        except FileNotFoundError:
            continue
        if len(candidate.strip()) >= config.MIN_LOCAL_CHARS:
            return candidate, kind
    return "", ""


# =========================================================================== #
# Stage 1: Ingestion
# =========================================================================== #

def ingest_documents(sources=None):
    """Fetch, clean, and tag every source.

    Returns a list of document dicts, one per successfully loaded source:
        {text, source, url, title, doc_type, date}

    A source that fails to load (network error, blocked, or empty after
    cleaning) logs a warning and is skipped rather than aborting the run.
    """
    sources = sources if sources is not None else config.SOURCES
    documents = []

    for spec in sources:
        text, origin = "", ""

        if spec.get("local_only"):
            # Blocked hosts / JS-only pages: read the stored copy directly, no
            # live fetch attempted.
            text, origin = _load_local(spec)
        else:
            # 1) Try the live source.
            try:
                live = clean_text(LOADERS[spec["loader"]](spec["url"]))
                if not _looks_unusable(live):
                    text, origin = live, "live"
            except Exception as exc:  # report and fall back
                print(f"[WARN] live fetch failed for {spec['title']!r}: {exc}",
                      file=sys.stderr)
            # 2) Fall back to a local copy if the live result was unusable.
            if not text:
                text, origin = _load_local(spec)

        if not text:
            print(f"[SKIP] {spec['title']!r}: no usable content "
                  f"(add documents/pdf/{spec.get('pdf', '?')})",
                  file=sys.stderr)
            continue

        documents.append({
            "text": text,
            "source": spec["source"],
            "url": spec["url"],
            "title": spec["title"],
            "doc_type": spec["doc_type"],
            "date": spec["date"],
        })
        print(f"[OK]   {spec['title']!r}: {len(text):,} chars ({origin})")

    return documents


# =========================================================================== #
# Stage 2: Chunking
# =========================================================================== #

def _slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "doc"


def _build_splitter(chunk_size, chunk_overlap, model_name):
    """RecursiveCharacterTextSplitter whose length is measured in tokens of the
    all-MiniLM-L6-v2 tokenizer, so no chunk can overflow the embedding model's
    256 word-piece limit (Chunking Strategy)."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=config.CHUNK_SEPARATORS,
    )


def chunk_documents(documents, chunk_size=config.CHUNK_SIZE,
                    chunk_overlap=config.CHUNK_OVERLAP,
                    model_name=config.EMBED_MODEL):
    """Split each document into overlapping token-bounded chunks.

    Each chunk dict carries the parent's metadata plus a unique `chunk_id`:
        {text, source, url, title, doc_type, date, chunk_id}
    """
    splitter = _build_splitter(chunk_size, chunk_overlap, model_name)
    chunks = []

    for doc_index, doc in enumerate(documents):
        doc_slug = f"{doc_index:02d}-{_slugify(doc['title'])}"
        pieces = splitter.split_text(doc["text"])
        for piece_index, piece in enumerate(pieces):
            piece = piece.strip()
            if not piece:
                continue
            chunks.append({
                "text": piece,
                "source": doc["source"],
                "url": doc["url"],
                "title": doc["title"],
                "doc_type": doc["doc_type"],
                "date": doc["date"],
                "chunk_id": f"{doc_slug}::chunk-{piece_index:03d}",
            })

    return chunks
