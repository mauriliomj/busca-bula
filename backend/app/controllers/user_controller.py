from fastapi import APIRouter, Depends

from app.dependencies.authentication import get_current_member
from app.models.tenant.user import User
from app.schemas.user_schema import UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def show_current_user(current_member: User = Depends(get_current_member)):
    return current_member
