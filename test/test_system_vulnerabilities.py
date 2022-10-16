import random
from typing import Awaitable, List

from httpx import AsyncClient
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch

from app.main import APP
from app.models import SuccessWriteItemModel
from custom_exceptions import (
    AccessDenied,
    AuthenticationFailed,
    CVEDoesNotExist,
    SystemVulnerabilityAlreadyExists,
    SystemVulnerabilityDoesNotExist,
)
from systems import (
    get_system_vulnerabilities,
    get_system_vulnerability,
    SystemVulnerabilitySeverity,
    SystemVulnerabilityState,
)
from utils import NISTResponse, NISTSeverity
from .conftest import MOCK_USER_WRITE_OWNER, MOCK_USER_WRITE_REPORTER


@pytest.mark.asyncio
async def test_add_update_vulnerability(
    write_system: str, user_write_owner_jwt: str, user_write_reporter_jwt: str
) -> None:
    add_error = SystemVulnerabilityAlreadyExists()
    update_error = SystemVulnerabilityDoesNotExist()
    cve = "cve-2022-1234"
    description = "Test vulnerability CVE-2022-1234"
    references = ["https://reference-cve-2022-1234.com"]
    vuln = await get_system_vulnerability(write_system, cve)
    assert vuln is None

    async with AsyncClient(app=APP, base_url="http://test") as client:
        # Add vulnerability flow
        with patch(
            "systems.domain.fetch_cve_info",
            return_value=NISTResponse(
                description=description,
                references=references,
                severity=NISTSeverity(severity="low", severity_score=3.5)
            )
        ):
            response = await client.post(
                f"/systems/{write_system}/report_vuln",
                headers={"Authentication": f"Bearer {user_write_owner_jwt}"},
                json={"cve": cve}
            )
            assert response.status_code == 201

            vuln = await get_system_vulnerability(write_system, cve)
            assert vuln is not None
            assert vuln.cve == cve
            assert vuln.description == description
            assert vuln.system_name == write_system
            assert vuln.added_by == MOCK_USER_WRITE_OWNER
            assert vuln.modified_by == MOCK_USER_WRITE_OWNER
            assert vuln.references == references
            assert vuln.severity == SystemVulnerabilitySeverity.LOW
            assert vuln.severity_score == 3.5
            assert vuln.state == SystemVulnerabilityState.OPEN

        response = await client.post(
            f"/systems/{write_system}/report_vuln",
            headers={"Authentication": f"Bearer {user_write_owner_jwt}"},
            json={"cve": cve}
        )
        assert response.status_code == 400

        response_json = response.json()
        assert response_json["detail"] == add_error.message

        # Update vulnerability flow
        response = await client.post(
            f"/systems/{write_system}/update_vuln_state",
            headers={"Authentication": f"Bearer {user_write_reporter_jwt}"},
            json={"cve": cve, "state": "remediated"}
        )
        assert response.status_code == 200

        vuln = await get_system_vulnerability(write_system, cve)
        assert vuln is not None
        assert vuln.cve == cve
        assert vuln.description == description
        assert vuln.system_name == write_system
        assert vuln.added_by == MOCK_USER_WRITE_OWNER
        assert vuln.modified_by == MOCK_USER_WRITE_REPORTER
        assert vuln.references == references
        assert vuln.severity == SystemVulnerabilitySeverity.LOW
        assert vuln.severity_score == 3.5
        assert vuln.state == SystemVulnerabilityState.REMEDIATED

        response = await client.post(
            f"/systems/{write_system}/update_vuln_state",
            headers={"Authentication": f"Bearer {user_write_reporter_jwt}"},
            json={"cve": "CVE-2022-12345", "state": "remediated"}
        )
        assert response.status_code == 400

        response_json = response.json()
        assert response_json["detail"] == update_error.message


async def _mock_gather(
    *coros: Awaitable[SuccessWriteItemModel]
) -> List[SuccessWriteItemModel]:
    results: List[SuccessWriteItemModel] = []
    for coro in coros:
        result = await coro
        results.append(result)

    return results


@pytest.mark.asyncio
async def test_add_update_vulnerabilities_bulk(
    write_system: str, user_write_owner_jwt: str, user_write_reporter_jwt: str
) -> None:
    add_error = CVEDoesNotExist()
    update_error = SystemVulnerabilityDoesNotExist()
    cves = ["cve-2022-12341", "cve-2022-12342", "cve-2022-12343"]
    vulns = await get_system_vulnerabilities(write_system)
    vulns_cves = [vuln.cve for vuln in vulns]
    assert not any(cve in vulns_cves for cve in cves)

    async with AsyncClient(app=APP, base_url="http://test") as client:
        with patch(
            "app.bulk.asyncio.gather",
            _mock_gather
        ):
            with patch(
                "systems.domain.fetch_cve_info",
                side_effect=[
                    NISTResponse(
                        description="Test vulnerability cve-2022-12341",
                        references=[
                            "https://reference1-cve-2022-12341",
                            "https://reference3-cve-2022-12341",
                        ],
                        severity=NISTSeverity(
                            severity="medium",
                            severity_score=5.2
                        )
                    ),
                    NISTResponse(
                        description="Test vulnerability cve-2022-12342",
                        references=[],
                        severity=None
                    ),
                    add_error
                ]
            ):
                response = await client.post(
                    f"/systems/{write_system}/report_vulns_bulk",
                    headers={
                        "Authentication": f"Bearer {user_write_owner_jwt}"
                    },
                    json=[{"cve": cve} for cve in cves]
                )
                assert response.status_code == 200

                response_json = response.json()
                assert {
                    "detail": "",
                    "item": "cve-2022-12341",
                    "success": True
                } in response_json
                assert {
                    "detail": "",
                    "item": "cve-2022-12342",
                    "success": True
                } in response_json
                assert {
                    "detail": add_error.message,
                    "item": "cve-2022-12343",
                    "success": False
                } in response_json

            vulns = await get_system_vulnerabilities(write_system)
            vulns_cves = [vuln.cve for vuln in vulns]
            assert all(
                cve in vulns_cves
                for cve in ["cve-2022-12341", "cve-2022-12342"]
            )

            for vuln in vulns:
                if vuln.cve == "cve-2022-12342":
                    assert vuln.severity == (
                        SystemVulnerabilitySeverity.UNKNOWN
                    )
                    assert vuln.severity_score is None

            response = await client.post(
                f"/systems/{write_system}/update_vulns_state_bulk",
                headers={
                    "Authentication": f"Bearer {user_write_reporter_jwt}"
                },
                json=[
                    {
                        "cve": cve,
                        "state": random.choice(["open", "remediated"])
                    }
                    for cve in cves
                ]
            )
            assert response.status_code == 200

            response_json = response.json()
            assert {
                "detail": "",
                "item": "cve-2022-12341",
                "success": True
            } in response_json
            assert {
                "detail": "",
                "item": "cve-2022-12342",
                "success": True
            } in response_json
            assert {
                "detail": update_error.message,
                "item": "cve-2022-12343",
                "success": False
            } in response_json


def test_add_update_vulnerabilities_no_authentication(
    client: TestClient, write_system: str
) -> None:
    error = AuthenticationFailed()
    payloads = [
        ("report_vuln", {"cve": "cve-2022-1234"}),
        (
            "report_vulns_bulk",
            [{"cve": "cve-2022-1234"}, {"cve": "cve-2022-12345"}]
        ),
        ("update_vuln_state", {"cve": "cve-2022-1234", "state": "remediated"}),
        (
            "update_vulns_state_bulk",
            [
                {"cve": "cve-2022-1234", "state": "open"},
                {"cve": "cve-2022-1234", "state": "remediated"}
            ],
        )
    ]
    for endpoint, payload in payloads:
        response = client.post(
            f"/systems/{write_system}/{endpoint}",
            json=payload
        )
        assert response.status_code == 401

        response_json = response.json()
        assert response_json["detail"] == error.message


def test_add_update_vulnerabilities_no_permissions(
    client: TestClient,
    write_system: str,
    user_write_viewer_jwt: str,
    user_read_owner_jwt: str
) -> None:
    error = AccessDenied()
    payloads = [
        ("report_vuln", {"cve": "cve-2022-1234"}),
        (
            "report_vulns_bulk",
            [{"cve": "cve-2022-1234"}, {"cve": "cve-2022-12345"}]
        ),
        ("update_vuln_state", {"cve": "cve-2022-1234", "state": "remediated"}),
        (
            "update_vulns_state_bulk",
            [
                {"cve": "cve-2022-1234", "state": "open"},
                {"cve": "cve-2022-1234", "state": "remediated"}
            ],
        )
    ]
    for user_jwt in [
        user_write_viewer_jwt,  # Insufficient permissions
        user_read_owner_jwt  # Does not belong to the system
    ]:
        for endpoint, payload in payloads:
            response = client.post(
                f"/systems/{write_system}/{endpoint}",
                headers={"Authentication": f"Bearer {user_jwt}"},
                json=payload
            )
            assert response.status_code == 403

            response_json = response.json()
            assert response_json["detail"] == error.message


def test_add_vulnerability_validations(
    client: TestClient, write_system: str, user_write_owner_jwt: str
) -> None:
    payloads = [
        ("report_vuln", {"cve": "vulnerability"}),  # Bad CVE
        ("report_vuln", {"cve": "CVE-22000-12344"}),  # Bad CVE
        (
            "update_vuln_state",
            {"cve": "CVE-2022-1234", "state": "closed"}  # Invalid state
        ),
    ]
    for endpoint, payload in payloads:
        response = client.post(
            f"/systems/{write_system}/{endpoint}",
            headers={"Authentication": f"Bearer {user_write_owner_jwt}"},
            json=payload
        )
        assert response.status_code == 422
