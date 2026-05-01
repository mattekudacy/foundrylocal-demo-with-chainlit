# How to run

1. Install foundrylocal on your local machine

- Windows

```bash
winget install Microsoft.FoundryLocal
```

- Mac

```bash
brew install microsoft/foundrylocal/foundrylocal
```

2. Clone the repo

```bash
git clone https://github.com/mattekudacy/foundrylocal-demo-with-chainlit.git
```

3. Install dependencies

```bash
pip install -r requirements.txt
# or
uv sync # if uv is avaialble
```

4. Run the project

```bash
chainlit run chat_assistant.py
```
