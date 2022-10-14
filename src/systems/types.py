from enum import Enum
from typing import List, NamedTuple, Optional, TypedDict


class SystemRoles(Enum):
    OWNER: str = "owner"
    REPORTER: str = "reported"
    VIEWER: str = "viewer"


class SystemVulnerabilitySeverity(Enum):
    UNKNOWN: str = "unknown"
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
    severity: SystemVulnerabilitySeverity
    severity_score: Optional[float]


class VulnerabilityDetails(NamedTuple):
    cve: str
    description: str
    references: List[str]
    severity: SystemVulnerabilitySeverity
    severity_score: Optional[float]
    state: SystemVulnerabilityState


class VulnerabilitySummary(NamedTuple):
    total_vulns: int = 0
    total_open_vulns: int = 0
    total_remediated_vulns: int = 0


class SeveritySummary(NamedTuple):
    severity: SystemVulnerabilitySeverity
    summary: VulnerabilitySummary
    details: Optional[List[VulnerabilityDetails]]


class SeveritySummaryDict(TypedDict):
    total_vulns: int
    total_open_vulns: int
    total_remediated_vulns: int
    details: List[VulnerabilityDetails]


class System(NamedTuple):
    created_by: str
    creation_date: str
    description: str
    name: str


class SystemSummary(NamedTuple):
    summary: VulnerabilitySummary
    summary_by_severity: List[SeveritySummary]


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
    modified_by: str
    modified_date: str
    references: List[str]
    severity: SystemVulnerabilitySeverity
    severity_score: Optional[float]
    state: SystemVulnerabilityState
    system_name: str


class SystemVulnerabilityToUpdate(NamedTuple):
    modified_by: str
    modified_date: str
    state: SystemVulnerabilityState
