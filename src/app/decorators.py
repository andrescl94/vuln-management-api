from contextlib import suppress
import functools
from typing import Awaitable, Callable, Dict, List, ParamSpec, TypeVar, cast

from fastapi import Request

from custom_exceptions import AccessDenied
from jwt_token import get_email_from_jwt
from systems import SystemRoles, get_system_user_role
from users import verify_user_jwt_token


P = ParamSpec("P")
R = TypeVar("R")


AUTH_MODEL: Dict[str, List[SystemRoles]] = {
    "systems_add_user": [SystemRoles.OWNER],
    "systems_add_vulnerability": [SystemRoles.OWNER, SystemRoles.REPORTER],
    "systems_update_vulnerability_state": [
        SystemRoles.OWNER, SystemRoles.REPORTER
    ],
}


def require_access(
    func: Callable[P, Awaitable[R]]
) -> Callable[P, Awaitable[R]]:

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        request = kwargs["request"]
        system_name = str(kwargs["system_name"]).lower()
        user_email = get_email_from_jwt(cast(Request, request))
        user_role = await get_system_user_role(system_name, user_email)
        if user_role in AUTH_MODEL[func.__name__]:
            return await func(*args, **kwargs)
        raise AccessDenied()

    return wrapper


def require_authentication(
    func: Callable[P, Awaitable[R]]
) -> Callable[P, Awaitable[R]]:

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        request = kwargs["request"]
        auth_header = getattr(request, "headers", {}).get("Authentication", "")
        if auth_header and len(auth_header.split(" ")) == 2:
            jwt_token = auth_header.split(" ")[1]
            token_verified: bool = False
            with suppress(BaseException):
                token_verified = await verify_user_jwt_token(jwt_token)
            if token_verified:
                return await func(*args, **kwargs)
        raise AccessDenied()

    return wrapper
