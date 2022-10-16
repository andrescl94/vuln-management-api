from typing import Dict, List, Optional, TypedDict, cast

from custom_exceptions import AccessDenied, AuthenticationFailed
from fastapi.testclient import TestClient
from systems.types import SystemVulnerabilitySeverity


class VulnerabilityDetailsDict(TypedDict):
    cve: str
    description: str
    references: List[str]
    severity: str
    severity_score: Optional[float]
    state: str


def test_get_vuln_summary(
    client: TestClient, read_system: str, user_read_owner_jwt: str
) -> None:
    response = client.get(
        f"/systems/{read_system}/get_vuln_summary",
        headers={"Authentication": f"Bearer {user_read_owner_jwt}"}
    )
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["summary"]["total_vulns"] == 5
    assert response_json["summary"]["total_open_vulns"] == 2
    assert response_json["summary"]["total_remediated_vulns"] == 3

    expected_results_by_severity = {
        severity.value: expected_result
        for severity, expected_result in zip(
            SystemVulnerabilitySeverity,
            [
                (1, 1, 0),
                (0, 0, 0),
                (1, 0, 1),
                (2, 1, 1),
                (1, 0, 1)
            ]
        )
    }
    for severity_summary in response_json["summary_by_severity"]:
        severity = severity_summary["severity"]
        assert severity in expected_results_by_severity
        assert severity_summary["details"] is None

        total_vulns, open_vulns, remediated_vulns = (
            expected_results_by_severity[severity]
        )
        summary = severity_summary["summary"]
        assert summary["total_vulns"] == total_vulns
        assert summary["total_open_vulns"] == open_vulns
        assert summary["total_remediated_vulns"] == remediated_vulns


def test_get_vuln_summary_detailed(
    client: TestClient, read_system: str, user_read_owner_jwt: str
) -> None:
    response = client.get(
        f"/systems/{read_system}/get_vuln_summary",
        headers={"Authentication": f"Bearer {user_read_owner_jwt}"},
        params={"detailed": True}
    )
    assert response.status_code == 200

    response_json = response.json()

    expected_details_by_severity: Dict[
        str, List[VulnerabilityDetailsDict]
    ]  = {
        severity.value: expected_result
        for severity, expected_result in zip(
            SystemVulnerabilitySeverity,
            [
                [
                    VulnerabilityDetailsDict(
                        cve="cve-2022-12343",
                        description="Test vulnerability cve-2022-12343",
                        references=[],
                        severity="unknown",
                        severity_score=None,
                        state="open"
                    )
                ],
                cast(List[VulnerabilityDetailsDict], []),
                [
                    VulnerabilityDetailsDict(
                        cve="cve-2022-12345",
                        description="Test vulnerability cve-2022-12345",
                        references=[],
                        severity="medium",
                        severity_score=5.0,
                        state="remediated"
                    )
                ],
                [
                    VulnerabilityDetailsDict(
                        cve="cve-2022-12341",
                        description="Test vulnerability cve-2022-12341",
                        references=[
                            "https://reference-1-cve-2022-12341.com"
                        ],
                        severity="high",
                        severity_score=8.7,
                        state="open"
                    ),
                    VulnerabilityDetailsDict(
                        cve="cve-2022-12342",
                        description="Test vulnerability cve-2022-12342",
                        references=[
                            "https://reference-1-cve-2022-12342.com",
                            "https://reference-2-cve-2022-12342.com"
                        ],
                        severity="high",
                        severity_score=8.2,
                        state="remediated"
                    )
                ],
                [
                    VulnerabilityDetailsDict(
                        cve="cve-2022-12344",
                        description="Test vulnerability cve-2022-12344",
                        references=[
                            "https://reference-1-cve-2022-12344/com"
                        ],
                        severity="critical",
                        severity_score=9.5,
                        state="remediated"
                    )
                ],
            ]
        )
    }
    for severity_summary in response_json["summary_by_severity"]:
        severity = severity_summary["severity"]
        assert severity in expected_details_by_severity
        assert all(
            details in severity_summary["details"]
            for details in expected_details_by_severity[severity]
        )


def test_get_vuln_summary_no_authentication(
    client: TestClient, read_system: str
) -> None:
    error = AuthenticationFailed()
    response = client.get(f"/systems/{read_system}/get_vuln_summary")
    assert response.status_code == 401

    response_json = response.json()
    assert response_json["detail"] == error.message


def test_get_vuln_summary_no_permissions(
    client: TestClient,
    read_system: str,
    user_write_viewer_jwt: str,
) -> None:
    error = AccessDenied()
    response = client.get(
        f"/systems/{read_system}/get_vuln_summary",
        headers={"Authentication": f"Bearer {user_write_viewer_jwt}"},
        params={"detailed": True}
    )
    assert response.status_code == 403

    response_json = response.json()
    assert response_json["detail"] == error.message


def test_get_vuln_summary_validations(
    client: TestClient, read_system: str, user_read_owner_jwt: str
) -> None:
    response = client.get(
        f"/systems/{read_system}/get_vuln_summary",
        headers={"Authentication": f"Bearer {user_read_owner_jwt}"},
        params={"detailed": "show"}
    )
    assert response.status_code == 422
