import asyncio
from asyncio.events import AbstractEventLoop
from typing import Generator

from fastapi.testclient import TestClient
from freezegun import freeze_time
import pytest
import pytest_asyncio

from app.main import APP
from app.models import VulnerabilityDetailsModel
from systems import add_system_user, create_system, SystemRoles
from systems.dal import add_system_vulnerability
from systems.types import CVEInfo, SystemVulnerabilitySeverity, SystemVulnerabilityState
from users import create_user


MOCK_USER_CREATE = "mockusercreate@gmail.com"
MOCK_USER_READ_OWNER = "mockuserreadowner@gmail.com"
MOCK_USER_READ_REPORTER_EXPIRED = "mockuserreadreporterexpired@gmail.com"
MOCK_USER_WRITE_OWNER = "mockuserwriteowner@gmail.com"
MOCK_USER_WRITE_REPORTER = "mockuserwritereporter@gmail.com"
MOCK_USER_WRITE_VIEWER = "mockuserwriteviewer@gmail.com"

MOCK_READ_SYSTEM = "read-system"
MOCK_WRITE_SYSTEM = "write-system"


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(APP)


@pytest_asyncio.fixture(scope="session")
async def user_create_jwt() -> str:
    name: str = "Mock User Create"
    user = await create_user(MOCK_USER_CREATE , name)
    return user.jwt


@pytest_asyncio.fixture(scope="session")
async def user_read_owner_jwt() -> str:
    name: str = "Mock User Read Owner"
    user = await create_user(MOCK_USER_READ_OWNER , name)
    return user.jwt


@pytest_asyncio.fixture(scope="session")
@freeze_time("2022-01-01 05:00:00", tz_offset=-5)
async def user_read_reporter_expired_jwt() -> str:
    name: str = "Mock User Read Reporter Expired"
    user = await create_user(MOCK_USER_READ_REPORTER_EXPIRED , name)
    return user.jwt


@pytest_asyncio.fixture(scope="session")
async def user_write_owner_jwt() -> str:
    name: str = "Mock User Write Owner"
    user = await create_user(MOCK_USER_WRITE_OWNER , name)
    return user.jwt


@pytest_asyncio.fixture(scope="session")
async def user_write_reporter_jwt() -> str:
    name: str = "Mock User Reporter Owner"
    user = await create_user(MOCK_USER_WRITE_REPORTER , name)
    return user.jwt


@pytest_asyncio.fixture(scope="session")
async def user_write_viewer_jwt() -> str:
    name: str = "Mock User Viewer Owner"
    user = await create_user(MOCK_USER_WRITE_VIEWER , name)
    return user.jwt


@pytest_asyncio.fixture(scope="session")
async def read_system() -> str:
    description = "Test system for reading purposes"
    system = await create_system(
        MOCK_READ_SYSTEM, description, MOCK_USER_READ_OWNER
    )
    await add_system_user(
        MOCK_READ_SYSTEM,
        MOCK_USER_READ_REPORTER_EXPIRED,
        SystemRoles.REPORTER,
        MOCK_USER_READ_OWNER
    )

    await asyncio.gather(
        *[
            add_system_vulnerability(
                system_name=MOCK_READ_SYSTEM,
                cve=details.cve,
                user_email=MOCK_USER_READ_OWNER,
                cve_info=CVEInfo(
                    description="Test vulnerability",
                    references=details.references,
                    severity=details.severity,
                    severity_score=details.severity_score
                ),
                state=details.state
            )
            for details in [
                VulnerabilityDetailsModel(
                    cve="cve-2022-12341",
                    description="Test vulnerability cve-2022-12341",
                    references=["https://reference-1-cve-2022-12341.com"],
                    severity=SystemVulnerabilitySeverity.HIGH,
                    severity_score=8.7,
                    state=SystemVulnerabilityState.OPEN
                ),
                VulnerabilityDetailsModel(
                    cve="cve-2022-12342",
                    description="Test vulnerability cve-2022-12342",
                    references=[
                        "https://reference-1-cve-2022-12342.com",
                        "https://reference-2-cve-2022-12342.com"
                    ],
                    severity=SystemVulnerabilitySeverity.HIGH,
                    severity_score=8.2,
                    state=SystemVulnerabilityState.REMEDIATED
                ),
                VulnerabilityDetailsModel(
                    cve="cve-2022-12343",
                    description="Test vulnerability cve-2022-12343",
                    references=[],
                    severity=SystemVulnerabilitySeverity.UNKNOWN,
                    severity_score=None,
                    state=SystemVulnerabilityState.OPEN
                ),
                VulnerabilityDetailsModel(
                    cve="cve-2022-12344",
                    description="Test vulnerability cve-2022-12344",
                    references=["https://reference-1-cve-2022-12344/com"],
                    severity=SystemVulnerabilitySeverity.CRITICAL,
                    severity_score=9.5,
                    state=SystemVulnerabilityState.REMEDIATED
                ),
                VulnerabilityDetailsModel(
                    cve="cve-2022-12345",
                    description="Test vulnerability cve-2022-12345",
                    references=[],
                    severity=SystemVulnerabilitySeverity.MEDIUM,
                    severity_score=5.0,
                    state=SystemVulnerabilityState.REMEDIATED
                )
            ]
        ]
    )
    return system.name


@pytest_asyncio.fixture(scope="session")
async def write_system() -> str:
    description = "Test system for writing purposes"
    system = await create_system(
        MOCK_WRITE_SYSTEM, description, MOCK_USER_WRITE_OWNER
    )
    await add_system_user(
        MOCK_WRITE_SYSTEM,
        MOCK_USER_WRITE_REPORTER,
        SystemRoles.REPORTER,
        MOCK_USER_WRITE_OWNER
    )
    await add_system_user(
        MOCK_WRITE_SYSTEM,
        MOCK_USER_WRITE_VIEWER,
        SystemRoles.VIEWER,
        MOCK_USER_WRITE_OWNER
    )
    return system.name
