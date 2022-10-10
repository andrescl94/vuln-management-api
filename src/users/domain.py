import binascii
import secrets
from typing import Optional, Tuple

from utils import get_now_timestamp
from .dal import (
    create_user as dal_create_user,
    get_user as dal_get_user,
)
from .jwt_token import generate_encrypted_jwt_token
from .types import JWTClaims, User, UserAccessToken


JTI_BYTE_LENGTH = 32
JWT_TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 7  # A week


def generate_access_token(user_email: str, user_name: str) -> UserAccessToken:
    now_timestamp = get_now_timestamp()
    expiration_timestamp = now_timestamp + JWT_TOKEN_EXPIRATION_TIME
    jti = binascii.hexlify(secrets.token_bytes(JTI_BYTE_LENGTH)).decode()
    jwt_claims = JWTClaims(
        exp=expiration_timestamp,
        iat=now_timestamp,
        jti=jti,
        name=user_name,
        sub=user_email
    )
    jwt_token = generate_encrypted_jwt_token(jwt_claims)
    return UserAccessToken(
        exp=expiration_timestamp, jti=jti, jwt=jwt_token
    )


async def create_user(
    user_email: str, user_name: str
) -> Tuple[User, UserAccessToken]:
    access_token = generate_access_token(user_email, user_name)
    user = await dal_create_user(
        user_email, user_name, access_token.jti, access_token.exp
    )
    return user, access_token


async def get_user(user_email: str) -> Optional[User]:
    return await dal_get_user(user_email)
