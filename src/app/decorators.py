import functools
from typing import Awaitable, Callable, Dict, List, ParamSpec, TypeVar

from starlette_context import context

from custom_exceptions import AccessDenied, AuthenticationFailed, MaxItemsLimit
from systems import SystemRoles, get_system_user_role


P = ParamSpec("P")
R = TypeVar("R")


AUTH_MODEL: Dict[str, List[SystemRoles]] = {
    "systems_get_vuln_summary": [
        SystemRoles.OWNER, SystemRoles.REPORTER, SystemRoles.VIEWER
    ],
    "systems_add_user": [SystemRoles.OWNER],
    "systems_add_vulnerabilities_bulk": [
        SystemRoles.OWNER, SystemRoles.REPORTER
    ],
    "systems_add_vulnerability": [SystemRoles.OWNER, SystemRoles.REPORTER],
    "systems_update_vulnerabilities_state_bulk": [
        SystemRoles.OWNER, SystemRoles.REPORTER
    ],
    "systems_update_vulnerability_state": [
        SystemRoles.OWNER, SystemRoles.REPORTER
    ],
}


def enforce_items_limit(
    func: Callable[P, Awaitable[R]]
) -> Callable[P, Awaitable[R]]:

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        for value in kwargs.values():
            if isinstance(value, list) and len(value) > 20:
                raise MaxItemsLimit()
        return await func(*args, **kwargs)

    return wrapper


def require_access(
    func: Callable[P, Awaitable[R]]
) -> Callable[P, Awaitable[R]]:

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        system_name = str(kwargs["system_name"]).lower()
        user_email = context["user_email"]
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
        user_email = context["user_email"]
        token_verified = context["token_verified"]
        if user_email is not None and token_verified:
            return await func(*args, **kwargs)
        raise AuthenticationFailed()

    return wrapper
