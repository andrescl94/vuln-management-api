from contextlib import suppress
import functools
from typing import Awaitable, Callable, ParamSpec, TypeVar

from fastapi.exceptions import HTTPException

from users import verify_user_jwt_token


P = ParamSpec("P")
R = TypeVar("R")


def require_authentication(
    func: Callable[P, Awaitable[R]]
) -> Callable[P, Awaitable[R]]:

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        request = kwargs["request"]
        auth_header = getattr(request, "headers", {}).get("Authentication", "")
        if auth_header and len(auth_header.split(" ", maxsplit=1)) == 2:
            jwt_token = auth_header.split(" ")[1]
            with suppress(BaseException):
                if await verify_user_jwt_token(jwt_token):
                    return await func(*args, **kwargs)
        raise HTTPException(status_code=401, detail="Access denied")

    return wrapper