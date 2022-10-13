from datetime import datetime
from typing import Dict, Any, List, Optional, TypedDict
import pytz

import aiohttp

from custom_exceptions import (
    CVEDoesNotExist,
    NISTAPIError,
)


NIST_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
TZ = pytz.timezone("America/Bogota")


class NISTResponse(TypedDict):
    description: str
    severity: Optional[str]
    severity_score: Optional[str]
    references: List[str]


async def fetch_cve_info(cve: str) -> NISTResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{NIST_URL}?cveId={cve.upper()}") as response:
            if response.status != 200:
                raise NISTAPIError()
            result = await response.json()
            if result["totalResults"] == 0:
                raise CVEDoesNotExist()

            vulnerability: Dict[str, Any] = result["vulnerabilities"][0]["cve"]
            print(vulnerability["references"])
            severity = get_severity_from_nist(vulnerability.get("metrics", {}))

            return NISTResponse(
                description=vulnerability["descriptions"][0]["value"],
                severity=severity["severity"] if severity else None,
                severity_score=(
                    severity["severity_score"] if severity else None
                ),
                references=[ref["url"] for ref in vulnerability["references"]]
            )


def get_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).astimezone(tz=TZ).replace(
        microsecond=0
    ).isoformat()


def get_now_as_iso() -> str:
    return datetime.now().astimezone(tz=TZ).replace(microsecond=0).isoformat()


def get_now_timestamp() -> float:
    return datetime.now().astimezone(tz=TZ).timestamp()


def get_severity_from_nist(item: Dict[str, Any]) -> Optional[Dict[str, str]]:
    severity: Optional[Dict[str, str]] = None
    if item:
        for cvss in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            if cvss in item:
                severity = {
                    "severity": str(
                        item[cvss][0]["cvssData"]["baseSeverity"]
                    ).lower(),
                    "severity_score": item[cvss][0]["cvssData"]["baseScore"]
                }
                break

    return severity
