from fastapi.testclient import TestClient

from custom_exceptions import AccessDenied, AuthenticationFailed, MaxItemsLimit
from systems import SystemRoles


def test_authentication_successful(
    client: TestClient,
    read_system: str,
    user_read_owner_jwt: str
) -> None:
    response = client.get(
        f"/systems/{read_system}/get_vuln_summary",
        headers={"Authentication": f"Bearer {user_read_owner_jwt}"}
    )
    assert response.status_code == 200


def test_authentication_failed(client: TestClient, read_system: str) -> None:
    error = AuthenticationFailed()
    response = client.get(f"/systems/{read_system}/get_vuln_summary",)
    assert response.status_code == 401

    response_json = response.json()
    assert response_json["detail"] == error.message


def test_authentication_token_expired(
    client: TestClient,
    read_system: str,
    user_read_reporter_expired_jwt: str,
) -> None:
    error = AuthenticationFailed()
    response = client.get(
        f"/systems/{read_system}/get_vuln_summary",
        headers={"Authentication": f"Bearer {user_read_reporter_expired_jwt}"}
    )
    assert response.status_code == 401

    response_json = response.json()
    assert response_json["detail"] == error.message


def test_access_to_system(
    client: TestClient,
    write_system: str,
    user_read_owner_jwt: str
) -> None:
    error = AccessDenied()
    response = client.get(
        f"/systems/{write_system}/get_vuln_summary",
        headers={"Authentication": f"Bearer {user_read_owner_jwt}"}
    )
    assert response.status_code == 403

    response_json = response.json()
    assert response_json["detail"] == error.message


def test_permission_model(
    client: TestClient,
    write_system: str,
    user_write_reporter_jwt: str
) -> None:
    error = AccessDenied()
    response = client.post(
        f"/systems/{write_system}/add_user",
        headers={"Authentication": f"Bearer {user_write_reporter_jwt}"},
        json={"email": "test@gmail.com", "role": SystemRoles.REPORTER.value}
    )
    assert response.status_code == 403

    response_json = response.json()
    assert response_json["detail"] == error.message


def test_bulk_operations_limit(
    client: TestClient,
    write_system: str,
    user_write_owner_jwt: str
) -> None:
    error = MaxItemsLimit()
    response = client.post(
        f"/systems/{write_system}/report_vulns_bulk",
        headers={"Authentication": f"Bearer {user_write_owner_jwt}"},
        json=[{"cve": f"cve-2022-123{idx}"} for idx in range(25)]
    )
    response_json = response.json()
    assert response.status_code == 400

    assert response_json["detail"] == error.message
