import os
from typing import Any, Tuple


class MissingEnvVar(BaseException):
    def __init__(self, args: Tuple[Any, ...]) -> None:
        self.message = f"Missing {args[0]} environmental variable"
        super().__init__(self.message)


try:
    OAUTH_GOOGLE_CLIENT_ID = os.environ["OAUTH_GOOGLE_CLIENT_ID"]
    OAUTH_GOOGLE_SECRET = os.environ["OAUTH_GOOGLE_SECRET"]
except KeyError as exc:
    raise MissingEnvVar(exc.args) from exc
