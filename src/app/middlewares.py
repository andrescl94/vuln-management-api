from contextlib import suppress
import logging
import logging.config
import time
from typing import Dict, Optional, Union
from uuid import uuid4

from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Scope, Send, Receive
from starlette_context import context
from starlette_context.middleware import ContextMiddleware

from custom_exceptions import CustomExternalException
from users import verify_user_jwt_token


LOGGING_CONFIG = {
    "disable_existing_loggers": False,
    "formatters": {
        "custom": {
            "class": "logging.Formatter",
            "datefmt": "%Y-%m-%d %I:%M:%S %p %Z",
            "format": "[%(levelname)s] %(asctime)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "custom",
            "level": logging.DEBUG,
        }
    },
    "loggers": {
        "src": {
            "handlers": ["console"],
            "level": logging.DEBUG
        }
    },
    "version": 1
}
logging.config.dictConfig(LOGGING_CONFIG)
LOGGER = logging.getLogger(__name__)


class CustomContextMiddleware(ContextMiddleware):
    async def set_context(
        self, request: Request
    ) -> Dict[str, Union[bool, Optional[str]]]:
        user_email: Optional[str] = None
        token_verified: bool = False
        auth_header: str = request.headers.get("Authentication", "")
        if auth_header and len(auth_header.split(" ")) == 2:
            jwt_token = auth_header.split(" ")[1]
            with suppress(BaseException):
                token_verified, user = await verify_user_jwt_token(jwt_token)
                if user is not None:
                    user_email = user.email
        return {
            "request_id": str(uuid4()),
            "token_verified": token_verified,
            "user_email": user_email,
        }


class LoggingMiddleware:  # pylint: disable=too-few-public-methods
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request_id: str = context["request_id"]
        user_email: Optional[str] = context["user_email"]
        token_verified: bool = context["token_verified"]
        start_time: float = time.time()
        end_time: float = 0.0
        LOGGER.info(
            (
                "req_id=%s ip=%s user=%s valid_token=%s method=%s path=%s "
                "querystring=%s"
            ),
            request_id,
            scope["client"][0],
            "Unauthenticated" if user_email is None else user_email,
            token_verified,
            scope["method"],
            scope["path"],
            scope["query_string"]
        )

        async def send_after_logging(message: Message) -> None:
            nonlocal end_time
            nonlocal request_id
            nonlocal start_time

            if message["type"] == "http.response.start":
                end_time = time.time()
                LOGGER.info(
                    "req_id=%s status_code=%s process_time=%s",
                    request_id,
                    message["status"],
                    end_time - start_time
                )

            await send(message)

        await self.app(scope, receive, send_after_logging)


async def wrapped_http_exception_handler(
    request: Request, exc: HTTPException
) -> Response:
    request_id = context["request_id"]
    if isinstance(exc, CustomExternalException):
        LOGGER.debug("req_id=%s extra=%s", request_id, exc.extra)

    return await http_exception_handler(request, exc)
