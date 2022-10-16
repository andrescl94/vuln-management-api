
from unittest.mock import patch

from fastapi.testclient import TestClient
from freezegun import freeze_time
from httpx import AsyncClient
import pytest

from app.main import APP
from custom_exceptions import ExternalAuthError
from users import get_user
from users.domain import JWT_TOKEN_EXPIRATION_TIME
from utils import get_from_timestamp, get_now_timestamp


def test_google_auth_redirect(client: TestClient) -> None:
    response = client.get("/login", allow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"].startswith(
        "https://accounts.google.com/o/oauth2/v2/auth"
    )


@pytest.mark.asyncio
async def test_google_auth_error() -> None:
    error = ExternalAuthError(("test",))
    with patch(
        "app.main._handle_oauth_response",
        side_effect=error
    ):
        async with AsyncClient(app=APP, base_url="http://test") as client:
            response = await client.get("/auth")
            assert response.status_code == 503

            response_json = response.json()
            assert response_json["detail"] == error.message


@pytest.mark.asyncio
@freeze_time("2022-01-01")
async def test_google_successful_auth() -> None:
    expected_expiration: str = get_from_timestamp(
        get_now_timestamp() + JWT_TOKEN_EXPIRATION_TIME
    )
    user_email: str = "mockuser@gmail.com"
    user_name: str = "Mock User"
    with patch(
        "app.main._handle_oauth_response",
        return_value={
            "userinfo": {
                "email": user_email,
                "name": user_name
            }
        }
    ):
        async with AsyncClient(app=APP, base_url="http://test") as client:
            response = await client.get("/auth")
            assert response.status_code == 201

            response_json = response.json()
            assert response_json["expiration_date"] == expected_expiration
            assert response_json["jwt_token"]

            user = await get_user(user_email)
            assert user is not None

            response = await client.get("/auth")
            response_json = response.json()
            assert response.status_code == 201
            assert response_json["expiration_date"] == expected_expiration
            assert response_json["jwt_token"] == None
