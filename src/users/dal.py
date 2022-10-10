from typing import Optional

from db import put_item, query
from utils import get_now_as_iso
from .types import User


async def create_user(
    user_email: str,
    user_name: str,
    access_token_jti: str,
    access_token_exp: float
) -> User:
    now = get_now_as_iso()
    user = User(
        access_token_exp=access_token_exp,
        access_token_jti=access_token_jti,
        email=user_email,
        last_login=now,
        name=user_name,
        registration_date=now
    )
    await put_item(
        f"USER#{user.email}",
        f"USER#{user.email}",
        **user._asdict()
    )

    return user


async def get_user(user_email: str) -> Optional[User]:
    user: Optional[User] = None
    results = await query(f"USER#{user_email}", f"USER#{user_email}")
    if results:
        user = User(
            access_token_exp=float(results[0]["access_token_exp"]),
            access_token_jti=results[0]["access_token_jti"],
            email=results[0]["email"],
            last_login=results[0]["last_login"],
            name=results[0]["name"],
            registration_date=results[0]["registration_date"],
        )

    return user
