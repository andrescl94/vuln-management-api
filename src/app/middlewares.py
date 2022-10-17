from contextlib import suppress
from typing import Dict, Optional, Union

from starlette.requests import Request
from starlette_context.middleware import ContextMiddleware

from users import verify_user_jwt_token


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
        return {"user_email": user_email, "token_verified": token_verified}
