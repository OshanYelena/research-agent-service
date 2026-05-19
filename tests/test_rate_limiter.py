from fastapi.testclient import TestClient

from app.core.rate_limiter import rate_limiter
from app.main import app

client = TestClient(app)


def test_rate_limiter_blocks_after_limit(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr("app.core.config.settings.RATE_LIMIT_REQUESTS", 1)
    monkeypatch.setattr("app.core.config.settings.RATE_LIMIT_WINDOW_SECONDS", 60)

    rate_limiter.requests.clear()

    first = client.post(
        "/research",
        json={
            "query": "summarize this article",
            "urls": ["https://example.com"],
        },
    )

    second = client.post(
        "/research",
        json={
            "query": "summarize this article",
            "urls": ["https://example.com"],
        },
    )

    assert first.status_code in {200, 500}
    assert second.status_code == 429

    data = second.json()

    assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "x-trace-id" in second.headers