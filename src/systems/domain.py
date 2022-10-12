from typing import Optional

from custom_exceptions import SystemAlreadyExists
from .dal import (
    create_user_access as dal_create_user_access,
    create_system as dal_create_system,
    get_system as dal_get_system,
)
from .types import System, SystemRoles


async def create_user_access(
    system_name: str, user_email: str, role: SystemRoles
) -> None:
    return await dal_create_user_access(system_name, user_email, role)


async def create_system(
    name: str, description: str, user_email: str
) -> System:
    system = await get_system(name)
    if system is not None:
        raise SystemAlreadyExists()
    system = await dal_create_system(name, description, user_email)
    await create_user_access(system.name, user_email, SystemRoles.OWNER)

    return system


async def get_system(name: str) -> Optional[System]:
    return await dal_get_system(name)
