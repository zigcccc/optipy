from fastapi import APIRouter, Depends

from todoist.api.deps import get_current_user

from .schemas import User as UserOut
from .models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_my_user(user: User = Depends(get_current_user)):
    return user
