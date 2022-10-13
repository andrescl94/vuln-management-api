from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from systems import SystemRoles


class PathTags(Enum):
    AUTH: str = "authentication"
    SYSTEMS: str = "systems"


class AccessTokenModel(BaseModel):  # pylint: disable=too-few-public-methods
    expiration_date: Optional[str]
    jwt_token: Optional[str]
    user_id: str


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


class SystemVulnerabilityModel(  # pylint: disable=too-few-public-methods
    BaseModel
):
    cve: str = Field(
        default=...,
        title="CVE ID of the vulnerability to report",
        max_length=20,
        regex=r"^(cve|CVE)\-\d{4}\-\d{4,}"
    )
