from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

from app.main import APP
from custom_exceptions import AuthenticationFailed, SystemAlreadyExists
from systems import get_system
from .conftest import MOCK_USER_CREATE


@pytest.mark.asyncio
async def test_create_system(user_create_jwt: str) -> None:
    error = SystemAlreadyExists()
    system_name: str = "test-system"
    system_description: str = "Test system"
    system = await get_system(system_name)
    assert system is None

    async with AsyncClient(app=APP, base_url="http://test") as client:
        response = await client.post(
            "/systems/create",
            headers={"Authentication": f"Bearer {user_create_jwt}"},
            json={"name": system_name, "description": system_description}
        )
        assert response.status_code == 201

        system = await get_system(system_name)
        assert system is not None
        assert system.name == system_name
        assert system_description == system_description
        assert system.created_by == MOCK_USER_CREATE

        response = await client.post(
            "/systems/create",
            headers={"Authentication": f"Bearer {user_create_jwt}"},
            json={"name": system_name, "description": system_description}
        )
        assert response.status_code == 400

        response_json = response.json()
        assert response_json["detail"] == error.message


def test_create_system_no_auth(client: TestClient) -> None:
    error = AuthenticationFailed()
    response = client.post(
        "/systems/create",
        json={"name": "testsystem", "description": "Test System"}
    )
    assert response.status_code == 401

    response_json = response.json()
    assert response_json["detail"] == error.message


def test_create_system_validations(
    client: TestClient, user_create_jwt: str
) -> None:
    kwargs = {
        "url": "/systems/create",
        "headers": {"Authentication": f"Bearer {user_create_jwt}"}
    }

    # System name too short
    response = client.post(
        **kwargs,
        json={"name": "test", "description": "Test System"}
    )
    assert response.status_code == 422

    # System name too long
    response = client.post(
        **kwargs,
        json={
            "name": "testsytem-testsystem-testsystem",
            "description": "Test System"
        }
    )
    assert response.status_code == 422

    # System with forbidden characters
    response = client.post(
        **kwargs,
        json={"name": "test$y$tem", "description": "Test System"}
    )
    assert response.status_code == 422

    # Description too short
    response = client.post(
        **kwargs,
        json={"name": "testsystem", "description": "Test"}
    )
    assert response.status_code == 422

    # Descrition with forbidden characters
    response = client.post(
        **kwargs,
        json={"name": "testsystem", "description": "Test $ystem"}
    )
    assert response.status_code == 422
