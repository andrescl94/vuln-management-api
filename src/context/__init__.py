from enum import Enum
import os

from custom_exceptions import MissingEnvVar


class Environment(Enum):
    DEV: str = "development"
    PROD: str = "production"


try:
    APP_ENVIRONMENT = Environment(
        os.environ.get("APP_ENVIRONMENT", "development")
    )
    JWE_ENCRYPTION_KEY = os.environ["JWE_ENCRYPTION_KEY"]
    JWT_SIGNING_KEY = os.environ["JWT_SIGNING_KEY"]
    OAUTH_GOOGLE_CLIENT_ID = os.environ["OAUTH_GOOGLE_CLIENT_ID"]
    OAUTH_GOOGLE_SECRET = os.environ["OAUTH_GOOGLE_SECRET"]
except KeyError as exc:
    raise MissingEnvVar(exc.args) from exc
