from typing import Self

import httpx

from ..config import Settings, get_settings


class OllamaClient:
    def __init__(self, settings: Settings | None = None, client: httpx.AsyncClient | None = None):
        self.settings = settings or get_settings()
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.settings.ollama_url, timeout=120.0)
            self._owns_client = True
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> Self:
        await self._get_client()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    async def health(self) -> dict:
        try:
            client = await self._get_client()
            resp = await client.get("/api/tags")
            resp.raise_for_status()
            models = [m.get("name", "") for m in resp.json().get("models", [])]
            return {
                "ok": True,
                "models": models,
                "llm_available": any(
                    m == self.settings.llm_model or m.startswith(self.settings.llm_model + ":")
                    for m in models
                ),
                "embed_available": any(
                    m == self.settings.embed_model or m.startswith(self.settings.embed_model + ":")
                    for m in models
                ),
            }
        except (httpx.HTTPError, ValueError, KeyError):
            return {"ok": False, "models": [], "llm_available": False, "embed_available": False}

    async def generate(self, prompt: str, system: str | None = None, json_mode: bool = False) -> str:
        client = await self._get_client()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload: dict = {
            "model": self.settings.llm_model,
            "messages": messages,
            "stream": False,
            "options": {"num_ctx": self.settings.num_ctx},
        }
        if json_mode:
            payload["format"] = "json"
        resp = await client.post("/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    async def embed(self, texts: list[str]) -> list[list[float]]:
        client = await self._get_client()
        resp = await client.post(
            "/api/embed",
            json={"model": self.settings.embed_model, "input": texts},
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]
