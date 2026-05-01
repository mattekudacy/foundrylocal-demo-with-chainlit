"""
Document Summarizer
Upload a .txt or .pdf file and choose a summary style:
  1. Bullet points
  2. Single paragraph
  3. Three key takeaways
"""
import tempfile
import os
import chainlit as cl
import openai
from foundry_local import FoundryLocalManager

ALIAS = "qwen2.5-0.5b"

manager = FoundryLocalManager(ALIAS)
client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key,
)
MODEL_ID = manager.get_model_info(ALIAS).id

STYLES = {
    "1": (
        "bullet",
        "Summarize the following document into concise bullet points. "
        "Group related points under clear headings.",
    ),
    "2": (
        "paragraph",
        "Summarize the following document in a single, concise paragraph.",
    ),
    "3": (
        "takeaways",
        "Extract the three most important takeaways from the following document. "
        "Present each as a numbered point with a short title and one-sentence explanation.",
    ),
}


def read_file(path: str, filename: str) -> str:
    """Return plain text from a .txt or .pdf file."""
    if filename.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            return "[pypdf not installed — cannot read PDF]"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("pending_text", None)
    cl.user_session.set("pending_filename", None)
    await cl.Message(
        content=(
            "Document Summarizer — running locally via Foundry Local (qwen2.5-0.5b)\n\n"
            "Upload a `.txt` or `.pdf` file and I'll summarize it.\n"
            "Then choose a style:\n"
            "- **1** — Bullet points\n"
            "- **2** — Single paragraph\n"
            "- **3** — Three key takeaways"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    pending_text = cl.user_session.get("pending_text")
    pending_filename = cl.user_session.get("pending_filename")

    # If user is choosing a style for an already-uploaded doc
    if pending_text and message.content.strip() in STYLES:
        style_key = message.content.strip()
        _, system_prompt = STYLES[style_key]

        async with cl.Step(name=f"Summarizing ({STYLES[style_key][0]})") as step:
            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": pending_text},
                ],
            )
            summary = response.choices[0].message.content
            step.output = "Done"

        await cl.Message(
            content=f"**Summary of `{pending_filename}` ({STYLES[style_key][0]}):**\n\n{summary}"
        ).send()
        await cl.Message(
            content="Upload another file or type **1**, **2**, or **3** for a different summary style."
        ).send()
        return

    # Handle file upload
    if message.elements:
        file_el = message.elements[0]
        filename = getattr(file_el, "name", "document")

        async with cl.Step(name="Reading document") as step:
            text = read_file(file_el.path, filename)
            word_count = len(text.split())
            step.output = f"{word_count} words extracted"

        if not text.strip():
            await cl.Message(content="Could not extract text from the file.").send()
            return

        # Truncate to avoid overwhelming a tiny model
        max_chars = 6000
        truncated = text[:max_chars]
        if len(text) > max_chars:
            truncated += "\n\n[... document truncated for length ...]"

        cl.user_session.set("pending_text", truncated)
        cl.user_session.set("pending_filename", filename)

        await cl.Message(
            content=(
                f"Loaded **{filename}** ({word_count} words).\n\n"
                "Choose a summary style:\n"
                "- **1** — Bullet points\n"
                "- **2** — Single paragraph\n"
                "- **3** — Three key takeaways"
            )
        ).send()
        return

    # Fallback: treat message text as the document itself
    if message.content.strip() and not message.content.strip() in STYLES:
        cl.user_session.set("pending_text", message.content)
        cl.user_session.set("pending_filename", "pasted text")
        await cl.Message(
            content=(
                "Got your text. Choose a summary style:\n"
                "- **1** — Bullet points\n"
                "- **2** — Single paragraph\n"
                "- **3** — Three key takeaways"
            )
        ).send()
        return

    await cl.Message(
        content="Please upload a `.txt` or `.pdf` file, or paste text directly."
    ).send()
