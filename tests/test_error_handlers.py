from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_validation_error_response_shape():
    response = client.post(
        "/research",
        json={
            "query": "AI",
            "urls": ["https://example.com"],
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Request validation failed"
    assert "details" in data["error"]
    assert "trace_id" in data["error"]


def test_404_error_response_shape():
    response = client.get("/does-not-exist")

    assert response.status_code == 404

    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "HTTP_ERROR"
    assert "trace_id" in data["error"]