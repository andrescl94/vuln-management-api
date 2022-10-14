from typing import Any, Dict, List

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
from systems import (
    add_system_user,
    add_system_vulnerability,
    create_system,
    update_system_vulnerability_state,
)
from users import create_user, get_user
from utils import get_from_timestamp
from .bulk import add_system_vulnerabilities_bulk
from .decorators import (
    enforce_items_limit,
    require_access,
    require_authentication,
)
from .models import (
    PathTags,
    SuccessModel,
    SuccessTokenModel,
    SuccessWriteItemModel,
    SystemModel,
    SystemUserModel,
    SystemVulnerabilityModel,
    UpdateSystemVulnerabilityModel,
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
    path="/systems/create",
    response_model=SuccessModel,
    status_code=201,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
async def systems_create(
    request: Request,
    system: SystemModel
) -> SuccessModel:
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
    await create_system(system.name.lower(), system.description, user_email)
    return SuccessModel(success=True)


@APP.post(
    path="/systems/{system_name}/add_user",
    response_model=SuccessModel,
    status_code=201,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
@require_access
async def systems_add_user(
    request: Request, system_name: str, user: SystemUserModel
) -> SuccessModel:
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
    await add_system_user(
        system_name.lower(), user.email.lower(), user.role, user_email
    )
    return SuccessModel(success=True)


@APP.post(
    path="/systems/{system_name}/report_vuln",
    response_model=SuccessModel,
    status_code=201,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
@require_access
async def systems_add_vulnerability(
    request: Request, system_name: str, vulnerability: SystemVulnerabilityModel
) -> SuccessModel:
    """
    **Requires authentication and system access with at least role reporter**

    Report a vulnerability with the provided information to the system
    - **cve**: CVE ID of the vulnerability to report
    """
    user_email = get_email_from_jwt(request)
    await add_system_vulnerability(
        system_name.lower(), vulnerability.cve.lower(), user_email
    )
    return SuccessModel(success=True)


@APP.post(
    path="/systems/{system_name}/report_vulns_bulk",
    response_model=List[SuccessWriteItemModel],
    status_code=200,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
@require_access
@enforce_items_limit
async def systems_add_vulnerabilities_bulk(
    request: Request,
    system_name: str,
    vulnerabilities: List[SystemVulnerabilityModel]
) -> List[SuccessWriteItemModel]:
    """
    **Requires authentication and system access with at least role reporter**

    Report vulnerabilities with the provided information to the system.
    There is a limit of 20 items per call

    - **cve**: CVE ID of the vulnerability to report

    Individual items may fail to be added,
    so be sure to check the response for more information
    """
    user_email = get_email_from_jwt(request)
    return await add_system_vulnerabilities_bulk(
        system_name.lower(),
        _remove_duplicates([vuln.cve.lower() for vuln in vulnerabilities]),
        user_email
    )


@APP.post(
    path="/systems/{system_name}/update_vuln_state",
    response_model=SuccessModel,
    status_code=200,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
@require_access
async def systems_update_vulnerability_state(
    request: Request,
    system_name: str,
    vulnerability: UpdateSystemVulnerabilityModel
) -> SuccessModel:
    """
    **Requires authentication and system access with at least role reporter**

    Update the state of a vulnerability, either to open it or to remediate it

    - **cve**: CVE ID of the vulnerability to update
    - **state**: New state of the vulnerability
        - **open**
        - **remediated**
    """
    user_email = get_email_from_jwt(request)
    await update_system_vulnerability_state(
        system_name.lower(),
        vulnerability.cve.lower(),
        vulnerability.state,
        user_email
    )
    return SuccessModel(success=True)


@APP.get(
    path="/auth", response_model=SuccessTokenModel, tags=[PathTags.AUTH.value]
)
async def auth(request: Request) -> SuccessTokenModel:
    """
    Endpoint used by Google OAuth after a successful authentication.

    It will only return the API token on the first successfull authentication.
    """
    try:
        token = await OAUTH.google.authorize_access_token(request)
    except OAuthError as exc:
        raise ExternalAuthError(exc.args) from exc

    user_info = token.get('userinfo')
    return await handle_user_login(user_info)


@APP.get(path="/login", status_code=302, tags=[PathTags.AUTH.value])
async def login(request: Request) -> Any:
    """
    Login/Sign up to the application using your Google account
    """
    redirect_uri = request.url_for('auth')
    return await OAUTH.google.authorize_redirect(request, redirect_uri)


async def handle_user_login(
    user_info: Dict[str, Any]
) -> SuccessTokenModel:
    user_email: str = user_info["email"]
    user_name: str = user_info.get("name", "")
    user = await get_user(user_email)
    if user is None:
        access_token = await create_user(user_email, user_name)
    expiration_date = user.access_token_exp if user else access_token.exp
    return SuccessTokenModel(
        success=True,
        expiration_date=get_from_timestamp(expiration_date),
        jwt_token=None if user else access_token.jwt
    )


def _remove_duplicates(items: List[str]) -> List[str]:
    unique_items: List[str] = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)

    return unique_items
