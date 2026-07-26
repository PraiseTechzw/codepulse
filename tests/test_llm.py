import json

from codepulse.llm import get_llm_summary


def test_get_llm_summary_uses_openrouter(monkeypatch):
    captured = {}

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def read(self):
            return json.dumps(self._payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(request, timeout=10):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.headers)
        captured["data"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            {"choices": [{"message": {"content": "OpenRouter summary"}}]}
        )

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr("codepulse.llm.urlopen", fake_urlopen)

    result = get_llm_summary("demo-project", 82, {"smells": {"details": {"hits": 1}}})

    assert result == "OpenRouter summary"
    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    content_type = captured["headers"].get("Content-Type") or captured["headers"].get(
        "Content-type"
    )
    assert content_type == "application/json"
    assert captured["data"]["model"] == "cohere/north-mini-code:free"
    assert captured["data"]["messages"][1]["role"] == "user"
