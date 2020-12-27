from enum import Enum
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ApiKey(BaseModel):
    id: UUID
    user_id: UUID
    role_id: Optional[UUID]
    name: str
    description: str
    key: Optional[bytearray]
    created: datetime
    last_used: Optional[datetime]
    enabled: bool
    visible: bool
    metadata: Optional[dict]

    class Config:
        orm_mode = True


class User(BaseModel):
    id: UUID
    username: str
    role_id: UUID
    last_login: Optional[datetime]
    password: Optional[bytearray]
    enabled: bool
    visible: bool
    created: datetime

    class Config:
        orm_mode = True


class UserRole(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


class AvailableUserRoles(str, Enum):
    admin = "admin"
    user = "user"
    readonly = "read-only"
    transport = "transport"
    nobody = "nobody"
