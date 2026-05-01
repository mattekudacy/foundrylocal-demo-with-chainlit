# Foundry Local Demo with Chainlit

A collection of local AI demo applications built with [Microsoft Foundry Local](https://github.com/microsoft/foundry-local) and [Chainlit](https://docs.chainlit.io). All models run entirely on your machine — no cloud API keys required.

## Demos

| Script | Description |
|---|---|
| `chat_assistant.py` | Conversational chat assistant with full message history |
| `document_summarizer.py` | Upload a `.txt` or `.pdf` file and summarize it in bullet points, a paragraph, or as key takeaways |
| `tool_calling.py` | AI assistant with built-in tool calling (weather lookup and calculator) |
| `voice_note_taker.py` | Upload an audio file, transcribe it with Whisper, and generate organized notes |

## Prerequisites

- **Python 3.10+**
- **Foundry Local** installed on your machine

### Install Foundry Local

**Windows:**
```bash
winget install Microsoft.FoundryLocal
```

**macOS:**
```bash
brew install microsoft/foundrylocal/foundrylocal
```

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/mattekudacy/foundrylocal-demo-with-chainlit.git
   cd foundrylocal-demo-with-chainlit
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Or, if you have [uv](https://docs.astral.sh/uv/) installed:

   ```bash
   uv sync
   ```

   > **Note:** The `document_summarizer.py` demo optionally requires `pypdf` for PDF support. Install it with `pip install pypdf`.

## Usage

Start any demo by passing the script name to `chainlit run`. Foundry Local will automatically download the required model on first run.

### Chat Assistant

A streaming chat assistant that maintains conversation history.

```bash
chainlit run chat_assistant.py
```

### Document Summarizer

Upload a `.txt` or `.pdf` file, then choose a summary style:
- **1** — Bullet points
- **2** — Single paragraph
- **3** — Three key takeaways

```bash
chainlit run document_summarizer.py
```

### Tool Calling

An assistant that can call tools to look up (simulated) weather or evaluate math expressions.

```bash
chainlit run tool_calling.py
```

Example prompts:
- *What's the weather in Tokyo?*
- *Calculate 123 * 456 + 789*

### Voice Note Taker

Upload an audio file (WAV, MP3, FLAC, or M4A). The app transcribes it using Whisper and generates organized notes.

```bash
chainlit run voice_note_taker.py
```

> **Note:** Whisper transcription requires a platform supported by Foundry Local's `whisper-tiny` model.

## Models Used

| Model | Used by |
|---|---|
| `qwen2.5-0.5b` | Chat assistant, document summarizer, tool calling, voice note taker |
| `whisper-tiny` | Voice note taker (audio transcription) |

Models are managed automatically by `FoundryLocalManager` and are downloaded on first use.

## Additional Resources

- [Foundry Local documentation](https://learn.microsoft.com/en-us/windows/ai/foundry-local/)
- [Foundry Local SDK (PyPI)](https://pypi.org/project/foundry-local-sdk/)
- [Chainlit documentation](https://docs.chainlit.io)
- [Chainlit GitHub](https://github.com/Chainlit/chainlit)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
