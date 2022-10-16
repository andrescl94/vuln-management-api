from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

from app.main import APP
from custom_exceptions import (
    AccessDenied,
    AuthenticationFailed,
    SystemUserAlreadyExists,
)
from systems import get_system_user, SystemRoles
from .conftest import MOCK_USER_WRITE_OWNER


@pytest.mark.asyncio
async def test_add_user(write_system: str, user_write_owner_jwt: str) -> None:
    error = SystemUserAlreadyExists()
    user_email = "new-system-user@gmail.com"
    user = await get_system_user(write_system, user_email)
    role = SystemRoles.VIEWER.value
    assert user is None

    async with AsyncClient(app=APP, base_url="http://test") as client:
        response = await client.post(
            f"/systems/{write_system}/add_user",
            headers={"Authentication": f"Bearer {user_write_owner_jwt}"},
            json={"email": user_email, "role": role}
        )
        assert response.status_code == 201

        user = await get_system_user(write_system, user_email)
        assert user is not None
        assert user.email == user_email
        assert user.system_name == write_system
        assert user.added_by == MOCK_USER_WRITE_OWNER
        assert user.role.value == role

        response = await client.post(
            f"/systems/{write_system}/add_user",
            headers={"Authentication": f"Bearer {user_write_owner_jwt}"},
            json={"email": user_email, "role": role}
        )
        assert response.status_code == 400

        response_json = response.json()
        assert response_json["detail"] == error.message


def test_add_user_no_auth(client: TestClient, write_system: str) -> None:
    error = AuthenticationFailed()
    response = client.post(
        f"/systems/{write_system}/add_user",
        json={"email": "user@gmail.com", "role": SystemRoles.REPORTER.value}
    )
    assert response.status_code == 401

    response_json = response.json()
    assert response_json["detail"] == error.message


def test_add_user_no_permissions(
    client: TestClient, write_system: str, user_write_reporter_jwt: str
) -> None:
    error = AccessDenied()
    response = client.post(
        f"/systems/{write_system}/add_user",
        headers={"Authentication": f"Bearer {user_write_reporter_jwt}"},
        json={"email": "user@gmail.com", "role": SystemRoles.VIEWER.value}
    )
    assert response.status_code == 403

    response_json = response.json()
    assert response_json["detail"] == error.message


def test_add_user_validations(
    client: TestClient, write_system: str, user_write_owner_jwt: str
) -> None:
    kwargs = {
        "url": f"/systems/{write_system}/add_user",
        "headers": {"Authentication": f"Bearer {user_write_owner_jwt}"}
    }

    # Invalid email
    response = client.post(
        **kwargs,
        json={"email": "user", "role": SystemRoles.OWNER.value}
    )
    assert response.status_code == 422

    # Invalid role
    response = client.post(
        **kwargs,
        json={"email": "user@gmail.com", "role": "role"}
    )
    assert response.status_code == 422
