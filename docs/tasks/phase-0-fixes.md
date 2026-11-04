# Task: Phase 0 — review fixes

Supervisor review of Phase 0 found these issues. Fix all of them. **Do not commit, push, or change branches.**

1. **Resource leak** — `OllamaClient` lazily creates an `httpx.AsyncClient` but never closes it; `/health/ollama` builds a new client per request. Add `aclose()` and `async with` support (`__aenter__`/`__aexit__`) that closes only a client the class created itself (not one passed in). Use `async with OllamaClient() as c:` in the route. Add a test that an injected client is NOT closed and an owned client IS closed.
2. **Deprecations** — replace `@app.on_event("startup")` with a FastAPI `lifespan` handler. Replace `datetime.utcnow` defaults in `models.py` with a timezone-aware UTC helper (`datetime.now(UTC)`). Test run should have no DeprecationWarnings from our code.
3. **Status badge is too coarse** — the HTMX fragment only shows online/offline. Show three states: green "Ollama: ready (qwen3:14b)" when both models are available; amber "Ollama: online — missing <model names>" (include the `ollama pull ...` command) when models are missing; red "Ollama: offline". Use `settings.llm_model` / `embed_model`, not hard-coded names. Escape any interpolated text (use a small Jinja partial template rather than f-string HTML). Add tests for all three states using a mocked `health()`.
4. **`start.ps1`** — (a) if Ollama is already running, the `OLLAMA_FLASH_ATTENTION` / `OLLAMA_KV_CACHE_TYPE` env vars are not applied to it: print a yellow warning explaining that and how to fix (quit Ollama from the tray and re-run, or set them as user env vars via `[Environment]::SetEnvironmentVariable(..., 'User')`). (b) Start the server, then poll `http://127.0.0.1:8000/health` (up to ~20s) before opening the browser, instead of opening it first.

## Done when
`uv run pytest -q` passes with no warnings originating from `studyforge/`, and `uv run ruff check .` is clean. Print a short summary.
