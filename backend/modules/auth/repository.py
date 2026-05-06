from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from backend.modules.auth.models import AuthEvent, LoginCode

class LoginCodeRepository:
    def __init__(self, db: Session):
        self.db=db
    def create(self, *, phone:str, code_hash: str, expires_at: datetime,)-> LoginCode:
        login_code=LoginCode(phone=phone, code_hash=code_hash, expires_at=expires_at,)
        self.db.add(login_code)
        self.db.flush()
        return login_code
    def get_active_by_phone(self, phone:str)->list[LoginCode]:
        return (self.db.query(LoginCode).filter(LoginCode.phone==phone, LoginCode.used_at.is_(None),).all())
    def get_latest_active_by_phone(self, phone:str)->LoginCode|None:
        return (self.db.query(LoginCode).filter(LoginCode.phone==phone, LoginCode.used_at.is_(None),).order_by(LoginCode.created_at.desc()).first())
    def invalidate_active_by_phone(self, *, phone:str, used_at:datetime,)->None:
        active_codes=self.get_active_by_phone(phone)
        for code in active_codes:
            code.used_at = used_at

class AuthEventRepository:
    def __init__(self, db: Session):
        self.db=db
    def create(self, *, event_type:str, phone:str|None=None, user_id:UUID|None=None, ip_address:str|None=None, user_agent:str|None=None,)->AuthEvent:
        event=AuthEvent(event_type=event_type, phone=phone, user_id=user_id, ip_address=ip_address, user_agent=user_agent)
        self.db.add(event)
        self.db.flush()
        return event
