import asyncio
from typing import Iterable, List

from custom_exceptions import CustomHTTPException
from systems import add_system_vulnerability

from .models import SuccessWriteItemModel


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


async def add_system_vulnerabilities_bulk(
    system_name: str, cves: Iterable[str], user_email: str
) -> List[SuccessWriteItemModel]:
    return await asyncio.gather(
        *[
            _add_system_vulnerability(system_name, cve, user_email)
            for cve in cves
        ]
    )
