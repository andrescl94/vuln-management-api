from enum import Enum
from typing import List, NamedTuple, Optional


class SystemRoles(Enum):
    OWNER: str = "owner"
    REPORTER: str = "reported"
    VIEWER: str = "viewer"


class SystemVulnerabilitySeverity(Enum):
    LOW: str = "low"
    MEDIUM: str = "medium"
    HIGH: str = "high"
    CRITICAL: str = "critical"


class SystemVulnerabilityState(Enum):
    OPEN: str = "open"
    REMEDIATED: str = "remediated"


class CVEInfo(NamedTuple):
    description: str
    references: List[str]
    severity: Optional[SystemVulnerabilitySeverity]
    severity_score: Optional[float]


class System(NamedTuple):
    created_by: str
    creation_date: str
    description: str
    name: str


class SystemUser(NamedTuple):
    added_date: str
    added_by: str
    email: str
    role: SystemRoles
    system_name: str


class SystemVulnerability(NamedTuple):
    added_by: str
    added_date: str
    cve: str
    description: str
    severity_hk: str
    state_hk: str
    modified_by: str
    modified_date: str
    references: List[str]
    severity_rk: Optional[str]
    state_rk: str
    severity: Optional[SystemVulnerabilitySeverity]
    severity_score: Optional[float]
    state: SystemVulnerabilityState
    system_name: str
