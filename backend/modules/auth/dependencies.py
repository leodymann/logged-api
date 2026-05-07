from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import decode_access_token
from backend.modules.users.models import User
from backend.modules.users.repository import UserRepository

bearer_scheme=HTTPBearer()
# Validar token e retornar usuário
def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(bearer_scheme),db:Session=Depends(get_db),)->User:
    token=credentials.credentials
    try:
        payload=decode_access_token(token)
        user_id=UUID(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token.",)
    repository=UserRepository(db)
    user=repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user unauthorized.",)
    return user