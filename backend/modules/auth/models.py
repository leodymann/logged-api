import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base

# Models de código de Login e eventos de autenticação

def utc_now()->datetime:
    return datetime.now(timezone.utc)

class LoginCode(Base):
    __tablename__ = "login_codes"
    id: Mapped[UUID]=mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,)
    phone: Mapped[str]=mapped_column(String(20), index=True, nullable=False,)
    code_hash: Mapped[str]=mapped_column(String(255), nullable=False,)
    expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), nullable=False,)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int]=mapped_column(Integer, default=0, nullable=False,)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utc_now, nullable=False,)

class AuthEvent(Base):
    __tablename__ = "auth_events"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, )
    phone: Mapped[str | None]=mapped_column(String(20) ,index=True ,nullable=True, )
    user_id: Mapped[uuid.UUID | None]=mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True, )
    event_type: Mapped[str]=mapped_column(String(50) ,index=True ,nullable=False, )
    ip_address: Mapped[str | None]=mapped_column( String(80), nullable=True, )
    user_agent: Mapped[str | None]=mapped_column(Text, nullable=True, )
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, )