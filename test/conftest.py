from fastapi.testclient import TestClient
import pytest

from app.main import APP


@pytest.fixture(autouse=False, scope="function")
def client() -> TestClient:
    return TestClient(APP)
