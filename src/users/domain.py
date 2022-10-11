import binascii
import secrets
from typing import Optional, Tuple


from jwt_token import (
    JWTClaims,
    decrypt_jwt_token,
    generate_encrypted_jwt_token,
)
from utils import get_now_timestamp
from .dal import (
    create_user as dal_create_user,
    get_user as dal_get_user,
)
from .types import User, UserAccessToken


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


async def verify_user_jwt_token(jwt_token: str) -> bool:
    jwt_verified: bool = False
    jwt_claims = decrypt_jwt_token(jwt_token)
    user = await get_user(jwt_claims.sub)
    if user:
        jwt_verified = (
            jwt_claims.jti == user.access_token_jti
            and get_now_timestamp() < user.access_token_exp
        )
    return jwt_verified


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
