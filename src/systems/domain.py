from typing import Optional

from custom_exceptions import SystemAlreadyExists, SystemUserAlreadyExists
from .dal import (
    add_system_user as dal_add_system_user,
    create_system as dal_create_system,
    get_system as dal_get_system,
    get_system_user as dal_get_system_user,
)
from .types import System, SystemRoles, SystemUser


async def add_system_user(
    system_name: str, email_to_add: str, role: SystemRoles, added_by: str
) -> SystemUser:
    system_user = await get_system_user(system_name, email_to_add)
    if system_user is not None:
        raise SystemUserAlreadyExists
    system_user = await dal_add_system_user(
        system_name, email_to_add, role, added_by
    )

    return system_user


async def create_system(
    name: str, description: str, user_email: str
) -> System:
    system = await get_system(name)
    if system is not None:
        raise SystemAlreadyExists()
    system = await dal_create_system(name, description, user_email)
    await add_system_user(
        system.name, user_email, SystemRoles.OWNER, user_email
    )

    return system


async def get_system(name: str) -> Optional[System]:
    return await dal_get_system(name)


async def get_system_user(
    system_name: str, email: str
) -> Optional[SystemUser]:
    return await dal_get_system_user(system_name, email)


async def get_system_user_role(
    system_name: str, user_email: str
) -> Optional[SystemRoles]:
    system_role: Optional[SystemRoles] = None
    system_user = await get_system_user(system_name, user_email)
    if system_user is not None:
        system_role = system_user.role

    return system_role
