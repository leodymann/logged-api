from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.modules.auth.schemas import (
    RequestCodeIn,
    RequestCodeOut,
    TokenOut,
    VerifyCodeIn,
)
from backend.modules.auth.service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/request-code", response_model=RequestCodeOut)
def request_code(payload:RequestCodeIn, request:Request, db:Session=Depends(get_db),):
    
    service = AuthService(db)
    try:
        service.request_code(
            raw_phone=payload.phone,
            ip_address=request.client.host if request.client else None, 
            user_agent=request.headers.get("user-agent"),
        )

        return {
            "message": "code sent to WhatsApp.",
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="we were unable to send the code via WhatsApp.",
        )
@router.post("/verify-code", response_model=TokenOut)
def verify_code(
    payload: VerifyCodeIn,
    request: Request,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    try:
        user, access_token = service.verify_code(
            raw_phone=payload.phone,
            code=payload.code,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )