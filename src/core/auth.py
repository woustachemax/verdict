from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta
from uuid import UUID
from src.config import settings
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from src.database import get_session
from src.models.user import User

password_hash = PasswordHash.recommended()
bearer = HTTPBearer()

def hash_password(password:str)->str:
    return password_hash.hash(password)

def verify_password(hashed:str, plain: str)->bool:
    return password_hash.verify(hashed, plain)

def generate_token(user_id: UUID)->str:
    now = datetime.utcnow
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(settings.JWT_EXPIRE_MINS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_token(token: str)->UUID:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, settings.JWT_EXPIRE_MINS)
        return UUID(payload["sub"])
    except(jwt.DecodeError, ValueError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")


def return_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_session)         
)->User:
    user_id = verify_token(creds.credentials)
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user