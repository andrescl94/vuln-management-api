from typing import NamedTuple


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
