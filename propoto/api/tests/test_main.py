from fastapi.testclient import TestClient

def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data

def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    # Check that our mocked env vars are detected
    assert data["environment"]["openrouter"] is True

def test_auth_success(client: TestClient, auth_headers):
    # Try a protected endpoint (even if it fails validation later, auth should pass)
    # We'll use a made-up endpoint or just check if we get 404 instead of 403
    # Or better, let's hit an actual endpoint with invalid data but valid auth
    response = client.post(
        "/agents/knowledge/ingest",
        headers=auth_headers,
        json={"url": "https://example.com"}
    )
    # It might fail due to mocking internal logic, but shouldn't be 403
    assert response.status_code != 403

def test_auth_failure(client: TestClient):
    response = client.post(
        "/agents/knowledge/ingest",
        headers={"x-api-key": "wrong-key"},
        json={"url": "https://example.com"}
    )
    assert response.status_code == 403
