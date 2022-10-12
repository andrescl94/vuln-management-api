from typing import Optional

from db import query, put_item
from utils import get_now_as_iso
from .types import System, SystemRoles


async def create_user_access(
    system_name: str, user_email: str, role: SystemRoles
) -> None:
    await put_item(
        f"SYSTEM#{system_name}",
        f"USER#{user_email}",
        role=role.value
    )


async def create_system(
    name: str, description: str, user_email: str
) -> System:
    now = get_now_as_iso()
    system = System(
        created_by=user_email,
        creation_date=now,
        description=description,
        name=name
    )
    await put_item(
        f"SYSTEM#{system.name}",
        f"SYSTEM#{system.name}",
        **system._asdict()
    )

    return system


async def get_system(name: str) -> Optional[System]:
    system: Optional[System] = None
    results = await query(f"SYSTEM#{name}", f"SYSTEM#{name}")
    if results:
        system = System(
            created_by=results[0]["created_by"],
            creation_date=results[0]["creation_date"],
            description=results[0]["description"],
            name=results[0]["name"]
        )

    return system
