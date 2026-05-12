from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_request_metadata_headers_are_added():
    response = client.get("/health")

    assert response.status_code == 200
    assert "x-trace-id" in response.headers
    assert "x-processing-time-ms" in response.headers


def test_trace_id_is_present_in_validation_error():
    response = client.post(
        "/research",
        json={
            "query": "AI",
            "urls": ["https://example.com"],
        },
    )

    data = response.json()

    assert response.status_code == 422
    assert data["error"]["trace_id"] is not None