from uuid import UUID
from sqlalchemy.orm import Session

from backend.modules.users.models import User

# Querys de usuário
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    def get_by_id(self, user_id:UUID)->User|None:
        return self.db.get(User, user_id)
    def get_by_phone(self, phone:str)->User|None:
        return(self.db.query(User).filter(User.phone==phone).first())
    def create(self, phone:str)->User:
        user = User(phone=phone)
        self.db.add(user)
        self.db.flush()
        return user