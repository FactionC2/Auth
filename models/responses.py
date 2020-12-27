from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: UUID
    username: str
    role_name: str
    enabled: bool
    visible: bool
    created: datetime
    last_login: Optional[datetime]


class LoginResponse(UserResponse):
    access_key: str


class VerifyResponse(UserResponse):
    api_key_name: str
    api_key_description: str


class HasuraVerifyResponse(BaseModel):
    user_id: str = Field(alias="X-Hasura-User-Id")
    user_role: str = Field(alias="X-Hasura-Role")
