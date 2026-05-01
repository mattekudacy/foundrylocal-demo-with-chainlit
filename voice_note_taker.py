"""
Voice-to-Text Note Taker
Upload an audio file (WAV/MP3/FLAC/M4A) and get organized notes.

Transcription uses Foundry Local's whisper-tiny model via the OpenAI
audio endpoint. Summarization uses qwen2.5-0.5b.
"""
import io
import chainlit as cl
import openai
from foundry_local import FoundryLocalManager

CHAT_ALIAS = "qwen2.5-0.5b"
WHISPER_ALIAS = "whisper-tiny"

# Start the service and load the chat model upfront
manager = FoundryLocalManager(CHAT_ALIAS)
chat_client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key,
)
CHAT_MODEL_ID = manager.get_model_info(CHAT_ALIAS).id

# Try to load whisper; not all platforms support it
try:
    manager.load_model(WHISPER_ALIAS)
    WHISPER_MODEL_ID = manager.get_model_info(WHISPER_ALIAS).id
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False


@cl.on_chat_start
async def on_chat_start():
    status = "whisper-tiny + qwen2.5-0.5b" if WHISPER_AVAILABLE else "qwen2.5-0.5b (no whisper on this platform)"
    await cl.Message(
        content=(
            f"Voice-to-Text Note Taker — running locally via Foundry Local\n"
            f"Models: {status}\n\n"
            "Upload an audio file (WAV, MP3, FLAC, M4A) to transcribe and summarize it into organized notes."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    if not message.elements:
        await cl.Message(content="Please attach an audio file (WAV, MP3, FLAC, or M4A).").send()
        return

    audio_file = next(
        (e for e in message.elements if isinstance(e, cl.Audio)),
        None,
    )
    if audio_file is None:
        # Also accept any file element and try treating it as audio
        audio_file = message.elements[0]

    await cl.Message(content="Processing your audio file...").send()

    # --- Transcription ---
    transcription = ""
    if WHISPER_AVAILABLE:
        async with cl.Step(name="Transcribing audio") as step:
            try:
                audio_client = openai.OpenAI(
                    base_url=manager.endpoint,
                    api_key=manager.api_key,
                )
                with open(audio_file.path, "rb") as f:
                    result = audio_client.audio.transcriptions.create(
                        model=WHISPER_MODEL_ID,
                        file=f,
                    )
                transcription = result.text
                step.output = f"Transcription complete ({len(transcription)} chars)"
            except Exception as e:
                step.output = f"Transcription failed: {e}"
                transcription = ""
    else:
        await cl.Message(
            content="Whisper is not available on this platform. Please paste the transcript as text instead."
        ).send()
        return

    if not transcription:
        await cl.Message(content="Could not transcribe the audio. Please try a different file.").send()
        return

    await cl.Message(content=f"**Transcript:**\n\n{transcription}").send()

    # --- Summarization into notes ---
    async with cl.Step(name="Generating notes") as step:
        response = chat_client.chat.completions.create(
            model=CHAT_MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a note-taking assistant. "
                        "Summarize the following transcription into organized, concise notes with bullet points. "
                        "Group related points under clear headings."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Transcription:\n\n{transcription}",
                },
            ],
        )
        notes = response.choices[0].message.content
        step.output = "Notes generated"

    await cl.Message(content=f"**Organized Notes:**\n\n{notes}").send()
