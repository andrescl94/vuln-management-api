from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from systems import (
    SystemRoles,
    SystemVulnerabilityState,
)
from systems.types import SystemVulnerabilitySeverity


class PathTags(Enum):
    AUTH: str = "authentication"
    SYSTEMS: str = "systems"


class SuccessModel(BaseModel):  # pylint: disable=too-few-public-methods
    success: bool


class SuccessWriteItemModel(  # pylint: disable=too-few-public-methods
    SuccessModel
):
    details: str
    item: str


class SuccessTokenModel(  # pylint: disable=too-few-public-methods
    SuccessModel
):
    expiration_date: Optional[str]
    jwt_token: Optional[str]


class SystemModel(BaseModel):  # pylint: disable=too-few-public-methods
    name: str = Field(
        default=...,
        min_length=5,
        max_length=25,
        title="Name of the system to create",
        regex=r"^[a-zA-Z0-9_\-]{5,25}$"
    )
    description: str = Field(
        default=...,
        min_length=5,
        max_length=55,
        title="Description of the system",
        regex=r"^[a-zA-Z0-9_\-\s]{5,55}$"
    )


class SystemUserModel(BaseModel):  # pylint: disable=too-few-public-methods
    email: EmailStr
    role: SystemRoles


class VulnerabilityDetailsModel(  # pylint: disable=too-few-public-methods
    BaseModel
):
    cve: str
    description: str
    references: List[str]
    severity: SystemVulnerabilitySeverity
    severity_score: Optional[float]
    state: SystemVulnerabilityState


class VulnerabilitySummaryModel(  # pylint: disable=too-few-public-methods
    BaseModel
):
    total_vulns: int
    total_open_vulns: int
    total_remediated_vulns: int


class SeveritySummaryModel(  # pylint: disable=too-few-public-methods
    BaseModel
):
    severity: SystemVulnerabilitySeverity
    summary: VulnerabilitySummaryModel
    details: Optional[List[VulnerabilityDetailsModel]]


class SystemSummaryModel(  # pylint: disable=too-few-public-methods
    BaseModel
):
    summary: VulnerabilitySummaryModel
    summary_by_severity: List[SeveritySummaryModel]


class SystemVulnerabilityModel(  # pylint: disable=too-few-public-methods
    BaseModel
):
    cve: str = Field(
        default=...,
        title="CVE ID of the vulnerability to report",
        max_length=20,
        regex=r"^(cve|CVE)\-\d{4}\-\d{4,}"
    )


class UpdateSystemVulnerabilityModel(  # pylint: disable=too-few-public-methods
    SystemVulnerabilityModel
):
    state: SystemVulnerabilityState
