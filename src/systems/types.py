from enum import Enum
from typing import NamedTuple


class System(NamedTuple):
    created_by: str
    creation_date: str
    description: str
    name: str


class SystemRoles(Enum):
    OWNER: str = "owner"
    REPORTER: str = "reported"
    VIEWER: str = "viewer"


class SystemUser(NamedTuple):
    added_date: str
    added_by: str
    email: str
    role: SystemRoles
    system_name: str
