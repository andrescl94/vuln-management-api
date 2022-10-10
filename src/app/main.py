from typing import Any, Dict

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware

from context import (
    OAUTH_GOOGLE_CLIENT_ID,
    OAUTH_GOOGLE_SECRET,
)
from users import User, create_user, get_user


APP = FastAPI()
APP.add_middleware(HTTPSRedirectMiddleware)
APP.add_middleware(
    SessionMiddleware,
    secret_key="secret",
    same_site="strcit",
    https_only=True
)

OAUTH = OAuth()
OAUTH.register(
    client_id=OAUTH_GOOGLE_CLIENT_ID,
    client_kwargs={
        "scope": "openid email profile"
    },
    client_secret=OAUTH_GOOGLE_SECRET,
    name="google",
    server_metadata_url=(
        "https://accounts.google.com/.well-known/openid-configuration"
    ),
)


@APP.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Hello World"}


@APP.get("/auth")
async def auth(request: Request) -> Dict[str, Any]:
    try:
        token = await OAUTH.google.authorize_access_token(request)
    except OAuthError:
        return {"message": "There was an error during authentication"}
    user_info = token.get('userinfo')
    logged_user = await handle_user_login(user_info)
    return {"message": logged_user}


@APP.get('/login')
async def login(request: Request) -> Any:
    redirect_uri = request.url_for('auth')
    return await OAUTH.google.authorize_redirect(request, redirect_uri)


async def handle_user_login(user_info: Dict[str, Any]) -> User:
    user_email: str = user_info["email"]
    user_name: str = user_info.get("name", "")
    user = await get_user(user_email)
    if user is None:
        user = await create_user(user_email, user_name)
    return user
