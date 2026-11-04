from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .db import init_db
from .generator.ollama_client import OllamaClient

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=BASE_DIR / "web" / "templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="StudyForge", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/health/ollama")
async def health_ollama(request: Request):
    async with OllamaClient() as client:
        result = await client.health()
    if request.headers.get("HX-Request"):
        settings = get_settings()
        missing = []
        if not result["llm_available"]:
            missing.append(settings.llm_model)
        if not result["embed_available"]:
            missing.append(settings.embed_model)
        return templates.TemplateResponse(
            request,
            "partials/ollama_status.html",
            {
                "ok": result["ok"],
                "llm_available": result["llm_available"],
                "embed_available": result["embed_available"],
                "llm_model": settings.llm_model,
                "embed_model": settings.embed_model,
                "missing": missing,
            },
        )
    return JSONResponse(result)
