from datetime import datetime
from typing import Dict, Any, List, NamedTuple, Optional
import pytz

import aiohttp

from custom_exceptions import (
    CVEDoesNotExist,
    NISTAPIError,
    NISTResponseError,
)


NIST_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
TZ = pytz.timezone("America/Bogota")


class NISTSeverity(NamedTuple):
    severity: str
    severity_score: float


class NISTResponse(NamedTuple):
    description: str
    references: List[str]
    severity: Optional[NISTSeverity]


async def fetch_cve_info(cve: str) -> NISTResponse:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{NIST_URL}?cveId={cve.upper()}"
            ) as response:
                if response.status != 200:
                    raise NISTResponseError()
                result = await response.json()
                if result["totalResults"] == 0:
                    raise CVEDoesNotExist()

                vulnerability: Dict[str, Any] = result["vulnerabilities"][0][
                    "cve"
                ]
                severity = get_severity_from_nist(
                    vulnerability.get("metrics", {})
                )

                return NISTResponse(
                    description=vulnerability["descriptions"][0]["value"],
                    severity=severity,
                    references=[
                        ref["url"] for ref in vulnerability["references"]
                    ]
                )
    except Exception as exc:
        if any(
            isinstance(exc, exec_type)
            for exec_type in [CVEDoesNotExist, NISTResponseError]
        ):
            raise exc
        raise NISTAPIError(exc.args) from exc


def get_from_timestamp(timestamp: float) -> str:
    return datetime.utcfromtimestamp(timestamp).astimezone(tz=TZ).replace(
        microsecond=0
    ).isoformat()


def get_now_as_iso() -> str:
    return get_from_timestamp(get_now_timestamp())


def get_now_timestamp() -> float:
    return datetime.utcnow().timestamp()


def get_severity_from_nist(item: Dict[str, Any]) -> Optional[NISTSeverity]:
    nist_severity: Optional[NISTSeverity] = None
    if item:
        for cvss in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            if cvss in item:
                severity: Optional[str] = item[cvss][0]["cvssData"].get(
                    "baseSeverity"
                )
                score = float(item[cvss][0]["cvssData"]["baseScore"])

                # baseSeverity attribute is not required in CVSS 2.0
                # https://csrc.nist.gov/schema/nvd/api/2.0/cvss-v2.0.json
                if severity is None:
                    if score < 4.0:
                        severity = "low"
                    elif score < 7.0:
                        severity = "medium"
                    else:
                        severity = "high"

                nist_severity = NISTSeverity(
                    severity=severity.lower(),
                    severity_score=score
                )
                break

    return nist_severity
