from typing import NamedTuple


class JWTClaims(NamedTuple):
    exp: float
    iat: float
    jti: str
    name: str
    sub: str


class User(NamedTuple):
    access_token_exp: float
    access_token_jti: str
    email: str
    last_login: str
    name: str
    registration_date: str


class UserAccessToken(NamedTuple):
    exp: float
    jti: str
    jwt: str
