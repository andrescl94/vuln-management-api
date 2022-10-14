import asyncio
from typing import List

from custom_exceptions import CustomHTTPException
from systems import add_system_vulnerability, update_system_vulnerability_state

from .models import SuccessWriteItemModel, UpdateSystemVulnerabilityModel


async def _add_system_vulnerability(
    system_name: str, cve: str, user_email: str
) -> SuccessWriteItemModel:
    success: bool = True
    details: str = ""
    try:
        await add_system_vulnerability(system_name, cve, user_email)
    except CustomHTTPException as exc:
        success = False
        details = exc.detail

    return SuccessWriteItemModel(
        item=cve, details=details, success=success
    )


async def _update_system_vulnerability_state(
    system_name: str,
    update: UpdateSystemVulnerabilityModel,
    user_email: str
) -> SuccessWriteItemModel:
    success: bool = True
    details: str = ""
    try:
        await update_system_vulnerability_state(
            system_name, update.cve, update.state, user_email
        )
    except CustomHTTPException as exc:
        success = False
        details = exc.detail

    return SuccessWriteItemModel(
        item=update.cve, details=details, success=success
    )


async def add_system_vulnerabilities_bulk(
    system_name: str, cves: List[str], user_email: str
) -> List[SuccessWriteItemModel]:
    return await asyncio.gather(
        *[
            _add_system_vulnerability(system_name, cve, user_email)
            for cve in cves
        ]
    )


async def update_system_vulnerabilities_state_bulk(
    system_name: str,
    updates: List[UpdateSystemVulnerabilityModel],
    user_email: str
) -> List[SuccessWriteItemModel]:
    return await asyncio.gather(
        *[
            _update_system_vulnerability_state(system_name, update, user_email)
            for update in updates
        ]
    )
