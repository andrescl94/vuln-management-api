from typing import Optional

from custom_exceptions import (
    SystemAlreadyExists,
    SystemUserAlreadyExists,
    SystemVulnerabilityAlreadyExists,
)
from utils import fetch_cve_info
from .dal import (
    add_system_user as dal_add_system_user,
    add_system_vulnerability as dal_add_system_vulnerability,
    create_system as dal_create_system,
    get_system as dal_get_system,
    get_system_user as dal_get_system_user,
    get_system_vulnerability as dal_get_system_vulnerability,
)
from .types import (
    CVEInfo,
    System,
    SystemRoles,
    SystemUser,
    SystemVulnerability,
    SystemVulnerabilitySeverity,
)


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


async def add_system_vulnerability(
    system_name: str, cve: str, user_email: str
) -> SystemVulnerability:
    system_vulnerability = await get_system_vulnerability(system_name, cve)
    if system_vulnerability is not None:
        raise SystemVulnerabilityAlreadyExists()

    if cve_data := await fetch_cve_info(cve):
        system_vulnerability = await dal_add_system_vulnerability(
            system_name,
            cve,
            user_email,
            CVEInfo(
                description=cve_data.description,
                references=cve_data.references,
                severity=(
                    SystemVulnerabilitySeverity(cve_data.severity.severity)
                    if cve_data.severity is not None else None
                ),
                severity_score=(
                    cve_data.severity.severity_score
                    if cve_data.severity is not None else None
                )
            )
        )

    return system_vulnerability


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


async def get_system_vulnerability(
    system_name: str, cve: str
) -> Optional[SystemVulnerability]:
    return await dal_get_system_vulnerability(system_name, cve)
