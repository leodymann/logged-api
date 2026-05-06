from fastapi import APIRouter, Depends

from backend.modules.auth.dependencies import get_current_user
from backend.modules.users.models import User
from backend.modules.users.schemas import UserOut

router=APIRouter(prefix="/users", tags=["Users"])
@router.get("/me", response_model=UserOut)
def get_me(current_user:User=Depends(get_current_user)):
    return current_user