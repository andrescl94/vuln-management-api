import asyncio
from asyncio.events import AbstractEventLoop
from typing import Generator

from fastapi.testclient import TestClient
from freezegun import freeze_time
import pytest
import pytest_asyncio

from app.main import APP
from systems import add_system_user, create_system, SystemRoles
from users import create_user


MOCK_USER_CREATE = "mockusercreate@gmail.com"
MOCK_USER_READ_OWNER = "mockuserreadowner@gmail.com"
MOCK_USER_READ_REPORTER_EXPIRED = "mockuserreadreporterexpired@gmail.com"
MOCK_USER_WRITE_OWNER = "mockuserwriteowner@gmail.com"
MOCK_USER_WRITE_REPORTER = "mockuserwritereporter@gmail.com"

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
    return system.name


@pytest_asyncio.fixture(scope="session")
async def write_system() -> str:
    description = "Test system for writing purposes"
    system = await create_system(
        MOCK_WRITE_SYSTEM, description, MOCK_USER_WRITE_OWNER
    )
    return system.name
