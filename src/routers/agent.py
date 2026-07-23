from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.agent.rbac_agent import evaluate_with_rust
from src.core.auth import return_user
from src.models.user import User

router = APIRouter()


class RBACRequest(BaseModel):
    action: str
    resource: str


class RBACResponse(BaseModel):
    allowed: bool
    decision: str
    reason: str
    role: str
    action: str
    resource: str


@router.post("/rbac", response_model=RBACResponse, status_code=status.HTTP_200_OK)
def evaluate_rbac(payload: RBACRequest, current_user: User = Depends(return_user)):
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role not in {"admin", "viewer"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unsupported role")

    if payload.action in {"read", "write", "delete"}:
        result = evaluate_with_rust(role=role, action=payload.action, resource=payload.resource)
        return result

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported action")
