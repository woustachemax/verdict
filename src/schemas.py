from datetime import datetime
from sqlmodel import SQLModel
from uuid import UUID

class UserRegister(SQLModel):
    name: str | None
    email: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserRead():
    id: UUID
    name: str
    email: str
    created_at: datetime
