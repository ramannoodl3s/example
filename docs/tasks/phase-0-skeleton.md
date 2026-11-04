# Task: Phase 0 — Project Skeleton

You are implementing Phase 0 of StudyForge. Read `DESIGN.md` first (sections 2, 4, 5, 8). Work only on the current git branch `feature/phase-0-skeleton`. **Do not commit, push, or change branches** — the supervisor handles git.

## Deliverables
1. **`pyproject.toml`** managed by `uv`. Python `>=3.12` (run `uv python install 3.12` if needed). Package name `studyforge`, src layout as in DESIGN.md §5 (top-level `studyforge/` package).
   - Runtime deps: fastapi, uvicorn[standard], jinja2, pydantic-settings, sqlalchemy>=2, httpx, pyyaml, typer.
   - Dev deps (dependency group `dev`): pytest, pytest-asyncio, ruff.
   - Console script: `studyforge = studyforge.cli:app` (Typer).
2. **`studyforge/config.py`** — `Settings` (pydantic-settings, env prefix `STUDYFORGE_`): `db_path` (default `data/studyforge.db`), `ollama_url` (`http://localhost:11434`), `llm_model` (`qwen3:14b`), `embed_model` (`nomic-embed-text`), `num_ctx` (32768), `request_delay_seconds` (3.0), `user_agent` (`StudyForge/0.1 (personal study tool)`).
3. **`studyforge/db.py` + `studyforge/models.py`** — SQLAlchemy 2.0 ORM for ALL tables in DESIGN.md §4 (embedding column can be `LargeBinary` for now). `init_db()` creates tables; creates the `data/` dir if missing.
4. **`studyforge/generator/ollama_client.py`** — async `OllamaClient` with `health()` (GET `/api/tags`, returns `{ok, models, llm_available, embed_available}`; never raises — returns ok=False on connection error), `generate(prompt, system=None, json_mode=False)` and `embed(texts)` using `/api/chat` and `/api/embed`, passing `options.num_ctx`.
5. **`studyforge/app.py`** — FastAPI app:
   - startup → `init_db()`
   - `GET /` → Jinja2 page (`studyforge/web/templates/base.html` + `index.html`) using Tailwind CDN and HTMX CDN, showing app title, a topic input box (non-functional placeholder), and an Ollama status badge loaded via HTMX from `/health/ollama`.
   - `GET /health` → `{"status":"ok"}`
   - `GET /health/ollama` → returns HTML fragment if `HX-Request` header present, else JSON from `health()`.
6. **`studyforge/cli.py`** — Typer app with `serve` (runs uvicorn on 127.0.0.1:8000) and `initdb`. Leave a `sites` sub-app stub (no commands yet) for Phase 1.
7. **`start.ps1`** — sets `$env:OLLAMA_FLASH_ATTENTION=1` and `$env:OLLAMA_KV_CACHE_TYPE="q8_0"`, starts `ollama serve` in background if not running, then `uv run studyforge serve` and opens the browser.
8. **Tests in `tests/`** (pytest): `/health` returns ok; `/` renders 200 and contains "StudyForge"; `init_db()` on a temp path creates all tables from §4; `OllamaClient.health()` returns ok=False (not an exception) when pointed at an unreachable port; mock-transport test that `generate()` sends `num_ctx`. Tests must NOT require a running Ollama.
9. **`README.md`** — short: what it is, prerequisites (uv, Ollama, `ollama pull qwen3:14b nomic-embed-text`), `./start.ps1`, how to run tests.

## Done when
- `uv sync` succeeds
- `uv run pytest -q` passes
- `uv run ruff check .` is clean

Run those three yourself before finishing, then print a short summary of files created.
