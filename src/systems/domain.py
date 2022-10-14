from typing import Dict, List, Optional

from custom_exceptions import (
    SystemAlreadyExists,
    SystemUserAlreadyExists,
    SystemVulnerabilityAlreadyExists,
    SystemVulnerabilityDoesNotExist,
)
from utils import fetch_cve_info, get_now_as_iso
from .dal import (
    add_system_user as dal_add_system_user,
    add_system_vulnerability as dal_add_system_vulnerability,
    create_system as dal_create_system,
    get_system as dal_get_system,
    get_system_user as dal_get_system_user,
    get_system_vulnerability as dal_get_system_vulnerability,
    get_system_vulnerabilities as dal_get_system_vulnerabilities,
    update_system_vulnerability as dal_update_system_vulnerability,
)
from .types import (
    CVEInfo,
    SeveritySummaryDict,
    VulnerabilityDetails,
    VulnerabilitySummary,
    SeveritySummary,
    System,
    SystemRoles,
    SystemSummary,
    SystemUser,
    SystemVulnerability,
    SystemVulnerabilitySeverity,
    SystemVulnerabilityState,
    SystemVulnerabilityToUpdate,
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
                    if cve_data.severity is not None
                    else SystemVulnerabilitySeverity("unkown")
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


async def get_system_summary(
    system_name: str, detailed: bool
) -> SystemSummary:
    vulns = await get_system_vulnerabilities(system_name)
    summary: Dict[str, SeveritySummaryDict] = {
        severity.name: {
            "total_vulns": 0,
            "total_open_vulns": 0,
            "total_remediated_vulns": 0,
            "details": []
        }
        for severity in SystemVulnerabilitySeverity
    }
    total_vulns: int = 0
    total_open_vulns: int = 0
    total_remediated_vuln: int = 0
    for vuln in vulns:
        summary[vuln.severity.name]["total_vulns"] += 1
        total_vulns += 1
        if vuln.state == SystemVulnerabilityState.OPEN:
            summary[vuln.severity.name]["total_open_vulns"] += 1
            total_open_vulns += 1
        elif vuln.state == SystemVulnerabilityState.REMEDIATED:
            summary[vuln.severity.name]["total_remediated_vulns"] += 1
            total_remediated_vuln += 1
        if detailed:
            summary[vuln.severity.name]["details"].append(
                VulnerabilityDetails(
                    cve=vuln.cve,
                    description=vuln.description,
                    references=vuln.references,
                    severity=vuln.severity,
                    severity_score=vuln.severity_score,
                    state=vuln.state
                )
            )

    return SystemSummary(
        summary=VulnerabilitySummary(
            total_vulns=total_vulns,
            total_open_vulns=total_open_vulns,
            total_remediated_vulns=total_remediated_vuln
        ),
        summary_by_severity=[
            SeveritySummary(
                severity=SystemVulnerabilitySeverity[severity],
                summary=VulnerabilitySummary(
                    total_vulns=severity_summary["total_vulns"],
                    total_open_vulns=severity_summary["total_open_vulns"],
                    total_remediated_vulns=severity_summary[
                        "total_remediated_vulns"
                    ],
                ),
                details=severity_summary["details"] if detailed else None
            )
            for severity, severity_summary in summary.items()
        ]
    )


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


async def get_system_vulnerabilities(
    system_name: str
) -> List[SystemVulnerability]:
    return await dal_get_system_vulnerabilities(system_name)


async def update_system_vulnerability_state(
    system_name: str,
    cve: str,
    state: SystemVulnerabilityState,
    user_email: str
) -> None:
    system_vulnerability = await get_system_vulnerability(system_name, cve)
    if system_vulnerability is None:
        raise SystemVulnerabilityDoesNotExist()

    if system_vulnerability.state != state:
        await dal_update_system_vulnerability(
            system_vulnerability.system_name,
            system_vulnerability.cve,
            SystemVulnerabilityToUpdate(
                modified_by=user_email,
                modified_date=get_now_as_iso(),
                state=state
            )
        )
