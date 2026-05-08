from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_research_endpoint_with_url():
    response = client.post(
        "/research",
        json={
            "query": "summarize this article",
            "urls": ["https://example.com"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "summarize this article"
    assert "summary" in data
    assert "sources" in data
    assert "trace_id" in data
    assert "summary_mode" in data
    assert "source_count" in data
    assert "failed_source_count" in data
    assert len(data["sources"]) == 1