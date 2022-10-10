import json

from jwcrypto import jwe, jwk
import jwt

from context import JWE_ENCRYPTION_KEY, JWT_SIGNING_KEY
from .types import JWTClaims


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
    jwe_claims = {
        "ciphertext": encrypted_object["ciphertext"],
        "encrypted_key": encrypted_object["encrypted_key"],
        "header": {
            "iv": encrypted_object["header"]["iv"],
            "tag": encrypted_object["header"]["tag"]
        },
        "iv": encrypted_object["iv"],
        "protected": encrypted_object["protected"],
        "tag": encrypted_object["tag"]
    }
    return jwt.encode(
        payload=jwe_claims,
        key=JWT_SIGNING_KEY,
        algorithm="HS512"
    )
