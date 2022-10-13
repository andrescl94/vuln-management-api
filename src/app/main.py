from typing import Any, Dict, Optional, Tuple

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from context import (
    OAUTH_GOOGLE_CLIENT_ID,
    OAUTH_GOOGLE_SECRET,
)
from custom_exceptions import ExternalAuthError
from jwt_token import get_email_from_jwt
from systems import add_system_user, add_system_vulnerability, create_system
from users import User, UserAccessToken, create_user, get_user
from utils import get_from_timestamp
from .decorators import require_access, require_authentication
from .models import (
    AccessTokenModel,
    PathTags,
    SystemModel,
    SystemUserModel,
    SystemVulnerabilityModel,
)


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


@APP.get(path="/", status_code=307)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse("/docs/")


@APP.post(
    path="/systems/create/",
    response_model=SystemModel,
    status_code=201,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
async def systems_create(
    request: Request,
    system: SystemModel
) -> SystemModel:
    """
    **Requires authentication**

    Creates a system to manage vulnerabilities with the provided information

    - **name**: Name of the system, restricted to alphanumeric characters,
      `-` (hyphen) and `_` (underscore); 5 to 25 characters long.
    - **description**: Description of the system,
      restricted to alphanumeric characters,
      `-` (hyphen), `_` (underscore) and ` ` (white speaces);
      5 to 55 characters long.
    """
    user_email = get_email_from_jwt(request)
    new_system = await create_system(
        system.name.lower(), system.description, user_email
    )
    return SystemModel(
        name=new_system.name, description=new_system.description
    )


@APP.post(
    path="/systems/{system_name}/add_user",
    response_model=SystemUserModel,
    status_code=201,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
@require_access
async def systems_add_user(
    request: Request, system_name: str, user: SystemUserModel
) -> SystemUserModel:
    """
    **Requires authentication and system access with role owner**

    Add a user to a system with the provided information

    - **email**: Email of the user to add
    - **role**: Role the user will have in said system
        - **owner**
        - **reporter**
        - **viewer**
    """
    user_email = get_email_from_jwt(request)
    added_user = await add_system_user(
        system_name.lower(), user.email.lower(), user.role, user_email
    )
    return SystemUserModel(email=added_user.email, role=added_user.role)


@APP.post(
    path="/systems/{system_name}/report_vuln",
    response_model=SystemVulnerabilityModel,
    status_code=201,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
@require_access
async def systems_add_vulnerability(
    request: Request, system_name: str, vulnerability: SystemVulnerabilityModel
) -> SystemVulnerabilityModel:
    """
    **Requires authentication and system access with at least role reporter**

    Report a vulnerability with the provided information to the system

    - **cve**: CVE ID of the vulnerability to report
    """
    user_email = get_email_from_jwt(request)
    added_vulnerability = await add_system_vulnerability(
        system_name, vulnerability.cve.lower(), user_email
    )
    return SystemVulnerabilityModel(cve=added_vulnerability.cve.upper())


@APP.get(
    path="/auth", response_model=AccessTokenModel, tags=[PathTags.AUTH.value]
)
async def auth(request: Request) -> AccessTokenModel:
    """
    Endpoint used by Google OAuth after a successful authentication.

    It will only return the API token on the first successfull authentication.
    """
    try:
        token = await OAUTH.google.authorize_access_token(request)
    except OAuthError as exc:
        raise ExternalAuthError() from exc

    user_info = token.get('userinfo')
    logged_user, access_token = await handle_user_login(user_info)
    response: AccessTokenModel
    if access_token is None:
        response = AccessTokenModel(user_id=logged_user.email)
    else:
        response = AccessTokenModel(
            user_id=logged_user.email,
            jwt_token=access_token.jwt,
            expiration_date=get_from_timestamp(access_token.exp)
        )

    return response


@APP.get(path="/login", status_code=302, tags=[PathTags.AUTH.value])
async def login(request: Request) -> Any:
    """
    Login/Sign up to the application using your Google account
    """
    redirect_uri = request.url_for('auth')
    return await OAUTH.google.authorize_redirect(request, redirect_uri)


async def handle_user_login(
    user_info: Dict[str, Any]
) -> Tuple[User, Optional[UserAccessToken]]:
    access_token: Optional[UserAccessToken] = None
    user_email: str = user_info["email"]
    user_name: str = user_info.get("name", "")
    user = await get_user(user_email)
    if user is None:
        user, access_token = await create_user(user_email, user_name)
    return user, access_token
