from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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
