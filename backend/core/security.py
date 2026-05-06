from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from backend.core.config import settings

def create_access_token(subject:str)->str:
    now=datetime.now(timezone.utc)
    payload={"sub":subject, "iat":now, "exp":now+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM,)
def decode_access_token(token:str)->dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM],)
    except JWTError as error:
        raise ValueError("Invalid Token.") from error