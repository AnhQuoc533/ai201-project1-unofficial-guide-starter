"""Grounded generation layer (Milestone 5).

generate_answer() formats the retrieved chunks into a numbered context block,
sends them with the grounded system prompt to Groq's llama-3.3-70b-versatile,
and returns the model's answer plus a deduplicated source list built from the
chunk metadata (for reliable clickable citations downstream).

The Groq API key is read from the GROQ_API_KEY environment variable. The client
is created lazily so importing this module never requires a key.
"""

import os
import config

_client = None


def _get_client():
    """Lazily create and cache the Groq client from GROQ_API_KEY."""
    global _client
    if _client is None:
        from groq import Groq  # imported lazily so import-time needs no key
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )
        _client = Groq(api_key=api_key)
    return _client


def format_context(chunks):
    """Render retrieved chunks as a numbered context block for the prompt."""
    blocks = []
    for i, c in enumerate(chunks, start=1):
        blocks.append(f"[{i}] (source: {c['title']} | {c['url']})\n{c['text']}")
    return "\n\n".join(blocks)


def dedupe_sources(chunks):
    """Unique (title, url) pairs from chunks, preserving retrieval order."""
    seen = set()
    sources = []
    for c in chunks:
        key = (c["title"], c["url"])
        if key not in seen:
            seen.add(key)
            sources.append({"title": c["title"], "url": c["url"]})
    return sources


def generate_answer(query, chunks, client=None):
    """Answer `query` grounded in `chunks`.

    Returns {"answer": str, "sources": [{"title", "url"}, ...]}. When no chunks
    are supplied (off-domain query / no match above the floor), returns the
    grounded refusal message without calling the model.
    """
    if not chunks:
        return {"answer": config.NO_CONTEXT_MESSAGE, "sources": []}

    client = client if client is not None else _get_client()
    user_message = (
        f"Context:\n{format_context(chunks)}\n\n"
        f"Question: {query}"
    )
    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        temperature=config.GROQ_TEMPERATURE,
        max_tokens=config.GROQ_MAX_TOKENS,
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    answer = response.choices[0].message.content.strip()

    # Model returns the sentinel when the retrieved context doesn't answer the
    # question: surface the refusal with no sources (avoids citing chunks that
    # were retrieved but didn't actually support an answer).
    if answer.strip("'\".").upper() == config.NO_ANSWER_TOKEN:
        return {"answer": config.NO_CONTEXT_MESSAGE, "sources": []}
    return {"answer": answer, "sources": dedupe_sources(chunks)}
