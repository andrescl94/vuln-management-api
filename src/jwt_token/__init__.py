import json
from typing import NamedTuple

from fastapi import Request
from jwcrypto import jwe, jwk
import jwt

from context import JWE_ENCRYPTION_KEY, JWT_SIGNING_KEY


class JWTClaims(NamedTuple):
    exp: float
    iat: float
    jti: str
    name: str
    sub: str


def decrypt_jwt_token(jwt_token: str) -> JWTClaims:
    jwe_claims = jwt.decode(
        jwt=jwt_token, key=JWT_SIGNING_KEY, algorithms=["HS512"]
    )
    _jwe = jwe.JWE()
    _jwe.deserialize(json.JSONEncoder().encode(jwe_claims))
    _jwe.decrypt(jwk.JWK().from_json(JWE_ENCRYPTION_KEY))
    decrypted_object = json.JSONDecoder().decode(_jwe.payload.decode("utf-8"))
    return JWTClaims(
        exp=decrypted_object["exp"],
        iat=decrypted_object["iat"],
        jti=decrypted_object["jti"],
        name=decrypted_object["name"],
        sub=decrypted_object["sub"]
    )


def generate_encrypted_jwt_token(jwt_claims: JWTClaims) -> str:
    claims_payload: bytes = json.JSONEncoder().encode(
        jwt_claims._asdict()
    ).encode("utf-8")
    encrypted_payload: str = jwe.JWE(
        plaintext=claims_payload,
        protected={
            "alg": "A256GCMKW",
            "enc": "A256GCM"
        },
        algs=["A256GCM", "A256GCMKW"],
        recipient=jwk.JWK.from_json(JWE_ENCRYPTION_KEY)
    ).serialize()
    encrypted_object = json.JSONDecoder().decode(encrypted_payload)
    return jwt.encode(
        payload=encrypted_object,
        key=JWT_SIGNING_KEY,
        algorithm="HS512"
    )


def get_email_from_jwt(request: Request) -> str:
    auth_header = request.headers["Authentication"]
    jwt_token = auth_header.split(" ")[1]
    jwt_claims = decrypt_jwt_token(jwt_token)
    return jwt_claims.sub
