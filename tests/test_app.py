from fastapi.testclient import TestClient

from studyforge.app import app

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_index_renders():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "StudyForge" in resp.text


def _hx_get(monkeypatch, health_result):
    class FakeOllamaClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc_info):
            return None

        async def health(self):
            return health_result

    monkeypatch.setattr("studyforge.app.OllamaClient", FakeOllamaClient)
    return client.get("/health/ollama", headers={"HX-Request": "true"})


def test_ollama_badge_ready(monkeypatch):
    resp = _hx_get(monkeypatch, {"ok": True, "llm_available": True, "embed_available": True})
    assert resp.status_code == 200
    assert "bg-green-100" in resp.text
    assert "Ollama: ready (qwen3:14b)" in resp.text


def test_ollama_badge_missing_models(monkeypatch):
    resp = _hx_get(monkeypatch, {"ok": True, "llm_available": False, "embed_available": False})
    assert "bg-amber-100" in resp.text
    assert "missing qwen3:14b, nomic-embed-text" in resp.text
    assert "ollama pull qwen3:14b &amp;&amp; ollama pull nomic-embed-text" in resp.text


def test_ollama_badge_offline(monkeypatch):
    resp = _hx_get(monkeypatch, {"ok": False, "llm_available": False, "embed_available": False})
    assert "bg-red-100" in resp.text
    assert "Ollama: offline" in resp.text
