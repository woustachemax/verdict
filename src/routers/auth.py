from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.schemas import UserRegister, UserLogin
from sqlmodel import Session, select
from src.database import get_session
from src.models.user import User
from src.core.auth import hash_password, verify_password, generate_token

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post('/register', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegister,
    session: Session = Depends(get_session),
):
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists, please login")

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = generate_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post('/login', response_model=TokenResponse)
def login(
    payload: UserLogin,
    session: Session = Depends(get_session)
):
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing is None or not verify_password(payload.password, existing.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials, try again or create a new account")

    token = generate_token(existing.id)
    return {"access_token": token, "token_type": "bearer"}