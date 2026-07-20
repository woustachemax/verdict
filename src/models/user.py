from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4

class Role(Enum):
    admin = "admin"
    viewer = "viewer"

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str | None
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    role: Role = Field(default=Role.viewer)