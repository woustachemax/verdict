from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel
from uuid import UUID

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefreshRequest(SQLModel):
    refresh_token: str

class UserRegister(SQLModel):
    name: str | None
    email: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserRead(SQLModel):
    id: UUID
    name: str
    email: str
    created_at: datetime
