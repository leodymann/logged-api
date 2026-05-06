import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base

def utc_now()->datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4,)
    phone: Mapped[str]=mapped_column(String(20), unique=True, index=True, nullable=False,)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utc_now, nullable=False,)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False,)
