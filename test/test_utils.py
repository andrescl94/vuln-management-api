from typing import Dict

import pytest
from unittest.mock import patch

from custom_exceptions import CVEDoesNotExist, NISTAPIError
from utils import (
    NISTResponse,
    NISTSeverity,
    get_severity_from_nist,
    fetch_cve_info
)


@pytest.mark.asyncio
async def test_fetch_cve_info() -> None:
    result = await fetch_cve_info("cve-2012-1234")
    assert result == NISTResponse(
        description=(
            "SQL injection vulnerability in Advantech/BroadWin WebAccess 7.0 "
            "allows remote authenticated users "
            "to execute arbitrary SQL commands via a malformed URL.  "
            "NOTE: this vulnerability exists because of an incomplete fix "
            "for CVE-2012-0234."
        ),
        references=[
            "http://www.us-cert.gov/control_systems/pdf/ICSA-12-047-01.pdf"
        ],
        severity=NISTSeverity(
            severity="medium",
            severity_score=6.5
        )
    )

    result = await fetch_cve_info("cve-2022-1234")
    assert result == NISTResponse(
        description=(
            "XSS in livehelperchat in GitHub repository "
            "livehelperchat/livehelperchat prior to 3.97. "
            "This vulnerability has the potential to deface websites, "
            "result in compromised user accounts, "
            "and can run malicious code on web pages, "
            "which can lead to a compromise of the userâ€™s device."
        ),
        references=[
            (
                "https://github.com/livehelperchat/livehelperchat/commit/"
                "a09aa0d793818dc4cae78ac4bcfb557d4fd2a30d"
            ),
            "https://huntr.dev/bounties/0d235252-0882-4053-85c1-b41b94c814d4"
        ],
        severity=NISTSeverity(
            severity="medium",
            severity_score=6.1
        )
    )

    with pytest.raises(CVEDoesNotExist):
        result = await fetch_cve_info("cve-2200-1234")

    with pytest.raises(NISTAPIError):
        with patch(
            "utils.aiohttp.ClientSession",
            return_value=Exception("Network error")
        ):
            result = await fetch_cve_info("cve-2022-1234")


@pytest.mark.parametrize(
    "metrics,expected_severity",
    [
        ({"cvssMetricV31": [{"cvssData": {"baseScore": 3.0}}]}, "low"),
        ({"cvssMetricV30": [{"cvssData": {"baseScore": 5.0}}]}, "medium"),
        ({"cvssMetricV2": [{"cvssData": {"baseScore": 8.0}}]}, "high")
    ]
)
def test_get_severity_from_nist(
    metrics: Dict[str, Dict[str, float]], expected_severity: str
) -> None:
    severity = get_severity_from_nist(metrics)
    assert severity is not None
    assert severity.severity == expected_severity
