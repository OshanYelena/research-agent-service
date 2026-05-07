from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_research_rejects_short_query():
    response = client.post(
        "/research",
        json={
            "query": "AI",
            "urls": ["https://example.com"],
        },
    )

    assert response.status_code == 422


def test_research_rejects_invalid_url():
    response = client.post(
        "/research",
        json={
            "query": "summarize this article",
            "urls": ["not-a-url"],
        },
    )

    assert response.status_code == 422