from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_research_endpoint():
    response = client.post(
        "/research",
        json={
            "query": "latest AI news"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "latest AI news"

    assert "summary" in data