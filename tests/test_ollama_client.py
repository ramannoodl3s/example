import json

import httpx
import pytest

from studyforge.config import Settings
from studyforge.generator.ollama_client import OllamaClient


@pytest.mark.asyncio
async def test_health_unreachable_returns_ok_false():
    settings = Settings(ollama_url="http://localhost:59999")
    client = OllamaClient(settings=settings)
    result = await client.health()
    assert result["ok"] is False
    assert result["models"] == []


@pytest.mark.asyncio
async def test_generate_sends_num_ctx():
    request_payloads = []

    def handler(request: httpx.Request) -> httpx.Response:
        request_payloads.append(request)
        return httpx.Response(200, json={"message": {"content": "hi"}})

    transport = httpx.MockTransport(handler)
    settings = Settings(num_ctx=32768)
    async with httpx.AsyncClient(transport=transport, base_url=settings.ollama_url) as http:
        client = OllamaClient(settings=settings, client=http)
        text = await client.generate("prompt", system="sys")
    assert text == "hi"
    body = json.loads(request_payloads[0].content)
    assert body["options"]["num_ctx"] == 32768


@pytest.mark.asyncio
async def test_aclose_closes_owned_client():
    client = OllamaClient(settings=Settings(ollama_url="http://localhost:59999"))
    http = await client._get_client()
    async with client:
        pass
    assert http.is_closed


@pytest.mark.asyncio
async def test_aclose_does_not_close_injected_client():
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    http = httpx.AsyncClient(transport=transport)
    client = OllamaClient(settings=Settings(), client=http)
    async with client:
        pass
    assert not http.is_closed
    await http.aclose()
