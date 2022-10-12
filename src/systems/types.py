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
