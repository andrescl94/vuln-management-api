from typing import Optional

from db import query, put_item, update_item
from utils import get_now_as_iso
from .types import (
    CVEInfo,
    System,
    SystemRoles,
    SystemUser,
    SystemVulnerability,
    SystemVulnerabilitySeverity,
    SystemVulnerabilityState,
    SystemVulnerabilityToUpdate,
)


async def add_system_user(
    system_name: str,
    email: str,
    role: SystemRoles,
    added_by: str
) -> SystemUser:
    system_user = SystemUser(
        added_date=get_now_as_iso(),
        added_by=added_by,
        email=email,
        role=role,
        system_name=system_name,
    )
    await put_item(
        f"SYSTEM#{system_user.system_name}",
        f"USER#{system_user.email}",
        **system_user._asdict()
    )

    return system_user


async def add_system_vulnerability(
    system_name: str, cve: str, user_email: str, cve_info: CVEInfo
) -> SystemVulnerability:
    now = get_now_as_iso()
    default_state = SystemVulnerabilityState.OPEN
    system_vulnerability = SystemVulnerability(
        added_by=user_email,
        added_date=now,
        cve=cve,
        description=cve_info.description,
        modified_by=user_email,
        modified_date=now,
        references=cve_info.references,
        severity=cve_info.severity,
        severity_score=cve_info.severity_score,
        state=default_state,
        system_name=system_name
    )
    await put_item(
        f"SYSTEM#{system_vulnerability.system_name}",
        f"CVE#{system_vulnerability.cve}",
        **system_vulnerability._asdict()
    )

    return system_vulnerability


async def create_system(
    name: str, description: str, user_email: str
) -> System:
    system = System(
        created_by=user_email,
        creation_date=get_now_as_iso(),
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


async def get_system_user(
    system_name: str, email: str
) -> Optional[SystemUser]:
    system_user: Optional[SystemUser] = None
    results = await query(f"SYSTEM#{system_name}", f"USER#{email}")
    if results:
        system_user = SystemUser(
            added_date=results[0]["added_date"],
            added_by=results[0]["added_by"],
            email=results[0]["email"],
            role=SystemRoles(results[0]["role"]),
            system_name=results[0]["system_name"]
        )

    return system_user


async def get_system_vulnerability(
    system_name: str, cve: str
) -> Optional[SystemVulnerability]:
    system_vulnerability: Optional[SystemVulnerability] = None
    results = await query(f"SYSTEM#{system_name}", f"CVE#{cve}")
    if results:
        system_vulnerability = SystemVulnerability(
            added_by=results[0]["added_by"],
            added_date=results[0]["added_date"],
            cve=results[0]["cve"],
            description=results[0]["description"],
            modified_by=results[0]["modified_by"],
            modified_date=results[0]["modified_date"],
            references=results[0]["references"],
            severity=(
                SystemVulnerabilitySeverity(results[0]["severity"])
                if results[0].get("severity")
                else None
            ),
            severity_score=(
                float(results[0]["severity_score"])
                if results[0].get("severity_score")
                else None
            ),
            state=SystemVulnerabilityState(results[0]["state"]),
            system_name=results[0]["system_name"]
        )

    return system_vulnerability


async def update_system_vulnerability(
    system_name: str,
    cve: str,
    update: SystemVulnerabilityToUpdate
) -> None:
    await update_item(
        f"SYSTEM#{system_name}", f"CVE#{cve}", **update._asdict()
    )
