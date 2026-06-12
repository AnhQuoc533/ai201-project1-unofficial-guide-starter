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
import os

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


def chat(message, history):
    """Chat handler used by Gradio's ChatInterface.

    Returns a single string (answer + optional sources).
    """
    message = message.strip()
    if not message:
        return ""
    chunks = retriever.retrieve(message)
    return generate.generate_answer(message, chunks)


def close_app():
    """Terminate the backend server immediately."""
    print("Closing app...")
    os._exit(0)


def build_ui():
    """Construct the Gradio Blocks UI modeled on the RulesBot design."""
    with gr.Blocks(
        title=config.APP_TITLE,
    ) as demo:

        gr.HTML(
            """
            <div style="text-align:center; padding:1.25rem 0 0.5rem;">
                <h1 style="font-size:2rem; font-weight:700; margin:0;">{title}</h1>
                <p style="font-size:1rem; margin:0.4rem 0 0;">{desc}</p>
            </div>
            """.format(title=config.APP_TITLE, desc=config.APP_DESCRIPTION)
        )

        with gr.Row():
            with gr.Column(scale=3):
                gr.ChatInterface(
                    fn=chat,
                    chatbot=gr.Chatbot(
                        height=440,
                        placeholder=(
                            "<div style='text-align:center; color:#9ca3af; margin-top:3rem;'>"
                            "Ask a question to get started — answers are grounded in the docs." 
                            "</div>"
                        ),
                    ),
                    textbox=gr.Textbox(
                        placeholder=(
                            "e.g. 'How can I get free food at GMU?'"
                        ),
                        container=False,
                        scale=7,
                    ),
                    examples=[[p] for p in getattr(config, "SUGGESTED_PROMPTS", [])],
                    cache_examples=False,
                )

            with gr.Column(scale=1, min_width=180):
                gr.HTML(
                    """
                    <div style="border-radius:10px; padding:1rem; margin-top:0.5rem;">
                        <p style="font-size:0.8rem; font-weight:700; margin:0 0 0.5rem; letter-spacing:0.05em;">📚 TOPICS</p>
                        <ul style="font-size:0.85rem; list-style:none; padding:0; margin:0; line-height:1.8;">
                            {items}
                        </ul>
                        <hr style="border:none; border-top:1px solid; margin:0.75rem 0;">
                        <p style="font-size:0.75rem; margin:0; line-height:1.5;">
                            Answers are grounded in the loaded documents only.
                        </p>
                    </div>
                    """.format(
                        items="\n".join(f"<li>{t}</li>" for t in getattr(config, "SUBTOPICS", []))
                    )
                )

                close_button = gr.Button("Close app", variant="stop")
                close_button.click(
                    fn=close_app,
                    inputs=[],
                    outputs=[],
                    js="() => { window.close(); }",
                )

    return demo


if __name__ == "__main__":
    load_dotenv()
    print("\n" + "=" * 80)
    print(f"  {config.APP_TITLE} — starting up")
    print("=" * 80 + "\n")
    ensure_index()
    build_ui().launch(theme=gr.themes.Soft(primary_hue="indigo"), inbrowser=True)

