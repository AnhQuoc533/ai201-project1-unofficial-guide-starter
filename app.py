"""Gradio interface for The Unofficial Guide (Milestone 5).

Wires the pipeline together: a user query is embedded and matched against the
ChromaDB collection (retriever), the top chunks are passed to the grounded
generator (generate), and the answer plus clickable source links are rendered.

This is the user-interface layer, so it is the one module with a CLI entry
point. Run it to serve the app locally:

    python app.py
"""

import gradio as gr
from dotenv import load_dotenv

import config
import generate
import ingest
import retriever


def ensure_index():
    """Return the populated collection, building it once if it doesn't exist."""
    try:
        collection = retriever.get_collection()
        if collection.count() > 0:
            return collection
    except Exception:
        pass  # collection missing — build it below
    chunks = ingest.chunk_documents(ingest.ingest_documents())
    return retriever.build_vector_store(chunks)


def format_sources(sources):
    """Render deduplicated sources as a markdown list of clickable links."""
    if not sources:
        return ""
    links = "\n".join(f"- [{s['title']}]({s['url']})" for s in sources)
    return f"**Sources**\n{links}"


def answer_query(query):
    """Retrieve + generate for one query. Returns (answer_md, sources_md)."""
    if not query or not query.strip():
        return "Please enter a question.", ""
    chunks = retriever.retrieve(query)
    result = generate.generate_answer(query, chunks)
    return result["answer"], format_sources(result["sources"])


def build_ui():
    """Construct the Gradio Blocks app (without launching it)."""
    with gr.Blocks(title=config.APP_TITLE) as demo:
        gr.Markdown(f"# {config.APP_TITLE}")
        gr.Markdown(config.APP_DESCRIPTION)
        gr.Markdown("**Sub-topics:** " + " · ".join(config.SUBTOPICS))

        query = gr.Textbox(
            label="Your question",
            placeholder="e.g. How can I get free food at GMU?",
            lines=2,
        )
        ask = gr.Button("Ask", variant="primary")
        answer = gr.Markdown(label="Answer")
        sources = gr.Markdown()

        gr.Examples(
            examples=[[p] for p in config.SUGGESTED_PROMPTS],
            inputs=query,
            label="Suggested questions",
        )

        ask.click(answer_query, inputs=query, outputs=[answer, sources])
        query.submit(answer_query, inputs=query, outputs=[answer, sources])
    return demo


def main():
    load_dotenv()
    ensure_index()
    build_ui().launch(
        server_name=config.SERVER_NAME,
        server_port=config.SERVER_PORT,
    )


if __name__ == "__main__":
    main()
