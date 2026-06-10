"""Central configuration for The Unofficial Guide RAG pipeline.

Every tunable constant lives here, grouped by the pipeline layer that uses it.
Layer modules (ingest, retriever, generate, app) import what they need from this
module so that values are defined in exactly one place.
"""

from pathlib import Path

# =========================================================================== #
# Project paths (shared)
# =========================================================================== #

PROJECT_ROOT = Path(__file__).resolve().parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
PDF_DIR = DOCUMENTS_DIR / "pdf"             # user-saved PDF fallbacks
SNAPSHOT_DIR = DOCUMENTS_DIR / "snapshots"  # hand-saved .txt fallbacks

# =========================================================================== #
# Embedding model (shared: governs chunk length now, embeddings in Milestone 4)
# =========================================================================== #

# all-MiniLM-L6-v2 accepts at most 256 word-piece tokens and emits 384-dim
# vectors. Its tokenizer is what measures chunk length during chunking.
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# =========================================================================== #
# Ingestion layer
# =========================================================================== #

# Browser-like User-Agent. Several hosts reject the default python-requests one.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 30  # seconds

# Below this many characters (after cleaning) we assume a LIVE fetch failed to
# capture real content (an empty SPA shell, a block page, etc.) and fall back to
# a local copy. Not applied to user-provided PDFs/snapshots, which are trusted.
MIN_USABLE_CHARS = 500

# A local copy (PDF/snapshot) only needs to be non-trivially non-empty; genuine
# sources can be short (e.g. a bus schedule), so we don't impose the SPA floor.
MIN_LOCAL_CHARS = 20

# The only doc_type values any chunk is allowed to carry.
APPROVED_DOC_TYPES = {
    "google_doc",     # shared Google Doc exported as plain text
    "reddit_thread",  # a Reddit post + its comments via the .json endpoint
    "gmu_page",       # an official George Mason department/program web page
    "athletics_page", # gomason.com athletics page
    "article",        # third-party editorial article
    "gov_page",       # local-government web page (City of Fairfax)
    "events_feed",    # Mason360 events listing
}

# Substrings that signal a page returned a block/SPA shell rather than content.
UNUSABLE_MARKERS = [
    "ad blocker detected",
    "enable javascript",
    "javascript is disabled",
    "please turn on javascript",
    "access denied",
    "are you a robot",
]

# The 10 sources from the Documents table in planning.md. "loader" selects the
# per-source-type loader; "date" is the access/publish date kept as provenance.
# Sources that can't be scraped (blocked hosts or JS-only pages) are marked
# "local_only": True and read straight from a stored "pdf" (or "snapshot") copy
# with no live fetch attempted; they need no "loader".
SOURCES = [
    {
        "source": "The Mason Everything Doc - Google Docs",
        "title": "The Mason Everything Doc",
        "doc_type": "google_doc",
        "url": "https://docs.google.com/document/d/11A-QRB7bBZ3XX3F3WJ8U0ZRLrEipKoB-9JLFMPf-oKU/",
        "date": "2026-06-09",
        "pdf": "00-google_doc.pdf",
        "local_only": True,  # use saved PDF; Google Doc text export retrieved poorly
    },
    {
        "source": "r/EngineeringStudents",
        "title": "Free stuff you can claim with your student email",
        "doc_type": "reddit_thread",
        "url": "https://www.reddit.com/r/EngineeringStudents/comments/1rphp2z/free_stuff_you_can_claim_with_your_student_email/",
        "date": "2026-06-09",
        "pdf": "02-reddit.pdf",
        "local_only": True,  # Reddit blocks non-browser traffic; use stored PDF
    },
    {
        "loader": "html",
        "source": "First-Gen+ Center - GMU",
        "title": "Perks and Discounts for GMU students",
        "doc_type": "gmu_page",
        "url": "https://firstgen.gmu.edu/resources-information/resource-guide-2/perks-discounts/",
        "date": "2026-06-09",
    },
    {
        "loader": "html",
        "source": "Student Support and Advocacy Center (SSAC)",
        "title": "Patriot Pantry",
        "doc_type": "gmu_page",
        "url": "https://ssac.gmu.edu/patriot-pantry",
        "date": "2026-06-09",
    },
    {
        "loader": "html",
        "source": "First-Year Connections - GMU",
        "title": "First-Year Programs",
        "doc_type": "gmu_page",
        "url": "https://fyc.gmu.edu/first-year-programs",
        "date": "2026-06-09",
    },
    {
        "loader": "html",
        "source": "Student Involvement - GMU",
        "title": "Mason Day",
        "doc_type": "gmu_page",
        "url": "https://si.gmu.edu/mason-day/",
        "date": "2026-06-09",
    },
    {
        "source": "George Mason University Athletics",
        "title": "Free Admission to George Mason athletic events",
        "doc_type": "athletics_page",
        "url": "https://gomason.com/sports/2013/8/1/205056605.aspx",
        "date": "2026-06-09",
        "pdf": "07-athletics.pdf",
        "snapshot": "07-athletics.txt",
        "local_only": True,  # JS page serves an ad-block shell; use local copy
    },
    {
        "loader": "html",
        "source": "The University Network",
        "title": "Affordable and Free Activities for GMU students in Fairfax, VA",
        "doc_type": "article",
        "url": "https://www.tun.com/schools/discover-affordable-and-free-activities-for-george-mason-university-students-in-fairfax-va",
        "date": "2026-06-09",
    },
    {
        "source": "City of Fairfax Virginia",
        "title": "CUE Bus",
        "doc_type": "gov_page",
        "url": "https://www.fairfaxva.gov/Services/CUE-Bus",
        "date": "2026-06-09",
        "pdf": "09-cue-bus.pdf",
        "local_only": True,  # WAF blocks non-browser traffic; use stored PDF
    },
    {
        "source": "Mason360",
        "title": "Mason360 Events",
        "doc_type": "events_feed",
        "url": "https://mason360.gmu.edu/events",
        "date": "2026-06-09",
        "pdf": "10-mason360.pdf",
        "local_only": True,  # JS-only events feed; use stored PDF
    },
]

# --- HTML extraction (ingestion layer) ------------------------------------- #

# Tags that never carry primary content; removed before text extraction.
STRIP_TAGS = [
    "script", "style", "noscript", "svg", "nav", "header", "footer",
    "aside", "form", "button", "iframe", "template",
]

# Candidate containers for the "real" page content, tried in priority order.
CONTENT_SELECTORS = [
    "main",
    "article",
    "[role=main]",
    "#main-content",
    "#main",
    "#content",
    ".main-content",
    ".content",
    ".page-content",
    ".entry-content",
]

# --- Text cleaning (ingestion layer) --------------------------------------- #

# Lines that are pure site furniture: nav, cookie banners, share widgets,
# accessibility skip-links, etc. Matched case-insensitively.
BOILERPLATE_PATTERNS = [
    r"skip to (main )?content",
    r"skip to navigation",
    r"back to top",
    r"^menu$",
    r"^search$",
    r"^close$",
    r"^home$",
    r"^login$",
    r"^log in$",
    r"^sign in$",
    r"^sign up$",
    r"accept all cookies",
    r"we use cookies",
    r"this (website|site) uses cookies",
    r"cookie (policy|preferences|settings)",
    r"privacy policy",
    r"terms of (use|service)",
    r"all rights reserved",
    r"^©",
    r"copyright \d{4}",
    r"share this",
    r"share on (facebook|twitter|x|linkedin)",
    r"follow us on",
    r"toggle navigation",
    r"^next$",
    r"^previous$",
    r"^prev$",
    r"javascript is (disabled|required)",
    r"enable javascript",
    r"loading\.\.\.",
    # SPA/template placeholder lines, e.g. "[eventName]", "[date_text]",
    # "[eventDates] [eventTimezone]", "([custom_time_instruction])".
    r"^[(\[]?(\[[A-Za-z0-9_]+\][\s)]*)+$",
    # A line that is only a (possibly open-paren) URL/path fragment, e.g.
    # "(/groups)", "(/webapp/auth/" — link cruft from rendered/PDF pages.
    r"^\(?/[^\s]*\)?$",
]

# Inline parenthesized relative-link references, e.g. "(/rsvp_boot?id=1&rel=x)".
INLINE_LINK_PATTERN = r"\(/[^)]*\)"

# Codepoint ranges of icon/emoji/CJK glyphs that misrendered web/PDF icons leave
# behind, plus the U+FFFD replacement char. This is an English-only corpus, so
# dropping these is safe; dashes, curly quotes and bullets (all below U+2190)
# are untouched. Built programmatically to avoid embedding raw glyphs here.
_ARTIFACT_RANGES = [
    (0x2190, 0x21FF),    # arrows
    (0x2300, 0x27BF),    # technical symbols + dingbats
    (0x2B00, 0x2BFF),    # misc symbols & arrows
    (0x3000, 0x9FFF),    # CJK punctuation + ideographs (misrendered icons)
    (0xF900, 0xFAFF),    # CJK compatibility ideographs
    (0xE000, 0xF8FF),    # private use area (icon fonts)
    (0xFFFD, 0xFFFD),    # replacement char from encoding errors
    (0x1F000, 0x1FAFF),  # emoji & pictographs
]
ARTIFACT_PATTERN = "[" + "".join(
    f"{chr(lo)}-{chr(hi)}" for lo, hi in _ARTIFACT_RANGES
) + "]"

# =========================================================================== #
# Chunking layer
# =========================================================================== #

CHUNK_SIZE = 256     # tokens (all-MiniLM-L6-v2 word-pieces)
CHUNK_OVERLAP = 38   # tokens (~15%)

# Per-doc_type overrides for sources whose structure needs finer granularity
# than the default. The Google Doc is a dense bullet list of many short items;
# at 256 tokens each chunk lumps ~10 items together and dilutes their embeddings,
# so specific queries (e.g. "Corner Pocket") can't match. Smaller chunks isolate
# each item. doc_types not listed here use CHUNK_SIZE / CHUNK_OVERLAP.
CHUNK_SIZE_OVERRIDES = {"google_doc": 80}
CHUNK_OVERLAP_OVERRIDES = {"google_doc": 12}  # ~15% of 80

# Split preference: paragraph, line, sentence, clause, word, then (last) char,
# so chunks land on natural boundaries before falling back to hard cuts.
CHUNK_SEPARATORS = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""]

# =========================================================================== #
# Embedding + retrieval layer (Milestone 4)
# =========================================================================== #

# Persistent ChromaDB store (gitignored). The collection holds one record per
# chunk: its 384-dim all-MiniLM-L6-v2 embedding + text + metadata.
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "unofficial_guide"
EMBEDDING_DIM = 384

# Cosine distance is the similarity metric (matches all-MiniLM-L6-v2 training).
DISTANCE_METRIC = "cosine"
EMBED_BATCH_SIZE = 64

# Retrieval defaults.
TOP_K = 5
# Cosine-similarity floor. Off-domain queries whose best matches fall below this
# return few/no chunks instead of 5 weak ones (so generation can refuse).
MIN_SIMILARITY = 0.30

# =========================================================================== #
# Generation + interface layer (Milestone 5)
# =========================================================================== #

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.2   # low: stay close to the retrieved context
GROQ_MAX_TOKENS = 1024

# Grounded system prompt: answer only from context; refuse with a sentinel when
# the answer isn't present (so the app can suppress the sources panel on refusal
# — the clickable sources are built separately from chunk metadata).
SYSTEM_PROMPT = (
    "You are The Unofficial Guide, an assistant that helps George Mason "
    "University students find free things, perks, events, and resources.\n\n"
    "Answer the question using ONLY the numbered context provided. Rules:\n"
    "- Be specific: include hours, locations, eligibility, costs, and step-by-"
    "step instructions when they appear in the context.\n"
    "- Preserve important notes, conditions, and warnings (e.g. ID required, "
    "limited spots, approximate times).\n"
    "- Do not use outside knowledge or guess. If the answer is not contained "
    'in the context, reply with exactly "NO_ANSWER" and nothing else.'
)

# Exact refusal token the model returns when the context lacks the answer.
NO_ANSWER_TOKEN = "NO_ANSWER"

# Shown when retrieval returns nothing usable or the model returns NO_ANSWER.
NO_CONTEXT_MESSAGE = (
    "I don't have information about that in my sources. I can help with free "
    "events, perks, discounts, food support, transportation, and activities "
    "for George Mason University students."
)

# --- Gradio interface ------------------------------------------------------ #

APP_TITLE = "The Unofficial Guide — Free Stuff for George Mason Students"
APP_DESCRIPTION = (
    "Ask about free events, perks, discounts, food support, transportation, "
    "and activities available to George Mason University students."
)

# Suggested questions surfaced in the UI (mirror the planning.md evaluation set).
SUGGESTED_PROMPTS = [
    "What is Mason Day and what will it feature in 2027?",
    "How can I enter Corner Pocket for free?",
    "Where and how can I get free food at GMU?",
    "What are the service hours of the CUE bus?",
    "How do I claim free tickets for GMU athletic events?",
]

# Sub-topics the corpus covers, shown as browsable hints in the UI.
SUBTOPICS = [
    "Free events", "Perks & discounts", "Food support", "Transportation",
    "Athletics", "First-year programs", "Arts & entertainment", "Student email perks",
]
