from typing import Optional

from .dal import (
    create_user as dal_create_user,
    get_user as dal_get_user,
)
from .types import User


async def create_user(user_email: str, user_name: str) -> User:
    return await dal_create_user(user_email, user_name)


async def get_user(user_email: str) -> Optional[User]:
    return await dal_get_user(user_email)
