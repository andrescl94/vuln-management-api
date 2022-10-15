from fastapi.testclient import TestClient


def test_root_redirect(client: TestClient) -> None:
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs/"
