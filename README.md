# StudyForge

A local-first study tool: you type in a certification or skill, StudyForge compares the top free tutorial sites, merges their lessons into one curriculum, and generates reading paths, flashcards and quizzes — all powered by a local LLM via Ollama. No API costs, data stays on your machine.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Ollama](https://ollama.com/) with the models pulled:

```powershell
ollama pull qwen3:14b
ollama pull nomic-embed-text
```

## Run

```powershell
./start.ps1
```

This sets the Ollama performance environment variables, starts `ollama serve` if it isn't running, launches the StudyForge web app on http://127.0.0.1:8000 and opens your browser.

Or manually:

```powershell
uv sync
uv run studyforge serve
```

## Tests

```powershell
uv run pytest -q
```
