# Unifers AI Agent

Local first Unifers sales intelligence agent.

## Run on Windows

1. Install Python 3.11 or newer.
2. Open this repository folder in Command Prompt.
3. Run `run_agent.bat`.
4. Open http://127.0.0.1:8000/docs for the API.
5. Open http://127.0.0.1:8000 for the chatbot UI.

## Optional local LLM

Install Ollama separately, then run:

`ollama pull qwen3:4b`

The agent automatically uses Ollama at `http://127.0.0.1:11434` when available. If Ollama is unavailable, the agent still works using the built in Unifers knowledge fallback.

Environment variables:

`OLLAMA_URL` defaults to `http://127.0.0.1:11434/api/chat`

`OLLAMA_MODEL` defaults to `qwen3:4b`

The original Streamlit app remains available as `app.py`.
