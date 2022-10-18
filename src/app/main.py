from typing import Any, Dict, List, Optional

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, Query, Request
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_context import context as request_context

from context import (
    OAUTH_GOOGLE_CLIENT_ID,
    OAUTH_GOOGLE_SECRET,
    SESSION_SECRET_KEY
)
from custom_exceptions import ExternalAuthError
from systems import (
    add_system_user,
    add_system_vulnerability,
    create_system,
    get_system_summary,
    update_system_vulnerability_state,
)
from users import create_user, get_user
from utils import get_from_timestamp
from .bulk import (
    add_system_vulnerabilities_bulk,
    update_system_vulnerabilities_state_bulk,
)
from .decorators import (
    enforce_items_limit,
    require_access,
    require_authentication,
)
from .middlewares import (
    CustomContextMiddleware,
    LoggingMiddleware,
    wrapped_http_exception_handler,
)
from .models import (
    PathTags,
    SeveritySummaryModel,
    SuccessModel,
    SuccessTokenModel,
    SuccessWriteItemModel,
    SystemModel,
    SystemSummaryModel,
    SystemUserModel,
    SystemVulnerabilityModel,
    UpdateSystemVulnerabilityModel,
    VulnerabilityDetailsModel,
    VulnerabilitySummaryModel,
)


MIDDLEWARES = [
    Middleware(
        SessionMiddleware,
        secret_key=SESSION_SECRET_KEY,
        same_site="strcit",
        https_only=True
    ),
    Middleware(CustomContextMiddleware),
    Middleware(LoggingMiddleware)
]
APP = FastAPI(
    exception_handlers={HTTPException: wrapped_http_exception_handler},
    middleware=MIDDLEWARES
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
async def systems_create(system: SystemModel) -> SuccessModel:
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
    user_email = request_context["user_email"]
    await create_system(system.name.lower(), system.description, user_email)
    return SuccessModel(success=True)


@APP.get(
    path="/systems/{system_name}/get_vuln_summary",
    response_model=SystemSummaryModel,
    status_code=200,
    tags=[PathTags.SYSTEMS.value]
)
@require_authentication
@require_access
async def systems_get_vuln_summary(
    system_name: str,
    detailed: bool = Query(
        default=False, title="Flag set to retrieve a more detailed report"
    )
) -> SystemSummaryModel:
    """
    **Requires authentication and system access**

    Returns a summary with all the vulnerabilities
    reported in the system and their current state,
    classified by severity

    - **detailed**: Boolean to set if you want to retrieve more details
    about the report
    """
    system_summary = await get_system_summary(system_name, detailed)
    return SystemSummaryModel(
        summary=VulnerabilitySummaryModel(
            total_vulns=system_summary.summary.total_vulns,
            total_open_vulns=system_summary.summary.total_open_vulns,
            total_remediated_vulns=(
                system_summary.summary.total_remediated_vulns
            )
        ),
        summary_by_severity=[
            SeveritySummaryModel(
                severity=severity_summary.severity,
                summary=VulnerabilitySummaryModel(
                    total_vulns=severity_summary.summary.total_vulns,
                    total_open_vulns=severity_summary.summary.total_open_vulns,
                    total_remediated_vulns=(
                        severity_summary.summary.total_remediated_vulns
                    )
                ),
                details=(
                    [
                        VulnerabilityDetailsModel(
                            cve=detail.cve,
                            description=detail.description,
                            references=detail.references,
                            severity=detail.severity,
                            severity_score=detail.severity_score,
                            state=detail.state
                        )
                        for detail in severity_summary.details
                    ]
                    if severity_summary.details is not None
                    else None
                )
            )
            for severity_summary in system_summary.summary_by_severity
        ]
    )


@APP.post(
    path="/systems/{system_name}/add_user",
    response_model=SuccessModel,
    status_code=201,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
@require_access
async def systems_add_user(
    system_name: str, user: SystemUserModel
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
    user_email = request_context["user_email"]
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
    system_name: str, vulnerability: SystemVulnerabilityModel
) -> SuccessModel:
    """
    **Requires authentication and system access with at least role reporter**

    Report a vulnerability with the provided information to the system
    - **cve**: CVE ID of the vulnerability to report
    """
    user_email = request_context["user_email"]
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
    user_email = request_context["user_email"]
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
    user_email = request_context["user_email"]
    await update_system_vulnerability_state(
        system_name.lower(),
        vulnerability.cve.lower(),
        vulnerability.state,
        user_email
    )
    return SuccessModel(success=True)


@APP.post(
    path="/systems/{system_name}/update_vulns_state_bulk",
    response_model=List[SuccessWriteItemModel],
    status_code=200,
    tags=[PathTags.SYSTEMS.value],
)
@require_authentication
@require_access
@enforce_items_limit
async def systems_update_vulnerabilities_state_bulk(
    system_name: str,
    vulnerabilities: List[UpdateSystemVulnerabilityModel]
) -> List[SuccessWriteItemModel]:
    """
    **Requires authentication and system access with at least role reporter**

    Update the state of vulnerabilities in bulk,
    either to open them or to remediate them

    - **cve**: CVE ID of the vulnerability to update
    - **state**: New state of the vulnerability
        - **open**
        - **remediated**
    """
    user_email = request_context["user_email"]
    return await update_system_vulnerabilities_state_bulk(
        system_name.lower(),
        _remove_duplicates(
            [
                UpdateSystemVulnerabilityModel(
                    cve=vuln.cve.lower(),
                    state=vuln.state
                )
                for vuln in vulnerabilities
            ]
        ),
        user_email
    )


@APP.get(
    path="/auth",
    response_model=SuccessTokenModel,
    status_code=201,
    tags=[PathTags.AUTH.value]
)
async def auth(request: Request) -> SuccessTokenModel:
    """
    Endpoint used by Google OAuth after a successful authentication.

    It will only return the API token on the first successfull authentication.
    """
    token = await _handle_oauth_response(request)
    user_info = token.get('userinfo')
    return await handle_user_login(user_info)


@APP.get(path="/login", status_code=302, tags=[PathTags.AUTH.value])
async def login(request: Request) -> Any:
    """
    Login/Sign up to the application using your Google account
    """
    redirect_uri = request.url_for('auth')
    return await OAUTH.google.authorize_redirect(request, redirect_uri)


async def _handle_oauth_response(request: Request) -> Any:
    try:
        token = await OAUTH.google.authorize_access_token(request)
    except OAuthError as exc:
        raise ExternalAuthError(exc.args) from exc

    return token


async def handle_user_login(
    user_info: Dict[str, Any]
) -> SuccessTokenModel:
    user_email: str = user_info["email"]
    user_name: str = user_info.get("name", "")
    jwt_token: Optional[str] = None
    token_expiration_date: Optional[float] = None

    user = await get_user(user_email)
    if user is None:
        access_token = await create_user(user_email, user_name)
        jwt_token = access_token.jwt
        token_expiration_date = access_token.exp
    else:
        token_expiration_date = user.access_token_exp
    return SuccessTokenModel(
        success=True,
        expiration_date=get_from_timestamp(token_expiration_date),
        jwt_token=jwt_token
    )


def _remove_duplicates(items: List[Any]) -> List[Any]:
    unique_items: List[Any] = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)

    return unique_items
