from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.core.security import create_access_token
from backend.modules.auth.repository import AuthEventRepository, LoginCodeRepository
from backend.modules.auth.utils import (
    generate_login_code,
    hash_code,
    normalize_phone_br,
    verify_code_hash,
)
from backend.modules.users.models import User
from backend.modules.users.repository import UserRepository
from backend.modules.integrations.whatsapp.client import WhatsAppClient


class AuthService:
    CODE_EXPIRATION_MINUTES = 5
    MAX_CODE_ATTEMPTS = 5

    def __init__(self, db: Session):
        self.db = db
        self.login_codes = LoginCodeRepository(db)
        self.auth_events = AuthEventRepository(db)
        self.users = UserRepository(db)
        self.whatsapp = WhatsAppClient()

    def request_code(
        self,
        *,
        raw_phone: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        phone = normalize_phone_br(raw_phone)
        now = datetime.now(timezone.utc)

        self.auth_events.create(
            event_type="CODE_REQUESTED",
            phone=phone,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.login_codes.invalidate_active_by_phone(
            phone=phone,
            used_at=now,
        )

        code = generate_login_code()

        self.login_codes.create(
            phone=phone,
            code_hash=hash_code(code),
            expires_at=now + timedelta(minutes=self.CODE_EXPIRATION_MINUTES),
        )

        message = (
            f"🔐 Seu código de acesso é: {code}\n\n"
            f"Ele expira em {self.CODE_EXPIRATION_MINUTES} minutos.\n\n"
            "Se você não solicitou este acesso, ignore esta mensagem."
        )

        try:
            self.whatsapp.send_text(
                to=phone,
                message=message,
            )

            self.auth_events.create(
                event_type="CODE_SENT",
                phone=phone,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            self.db.commit()

        except Exception:
            self.auth_events.create(
                event_type="CODE_SEND_FAILED",
                phone=phone,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.commit()
            raise

    def verify_code(
        self,
        *,
        raw_phone: str,
        code: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, str]:
        phone = normalize_phone_br(raw_phone)
        now = datetime.now(timezone.utc)

        login_code = self.login_codes.get_latest_active_by_phone(phone)

        if login_code is None:
            self.auth_events.create(
                event_type="CODE_INVALID",
                phone=phone,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.commit()
            raise ValueError("Código inválido ou expirado.")

        if login_code.expires_at < now:
            login_code.used_at = now

            self.auth_events.create(
                event_type="CODE_EXPIRED",
                phone=phone,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.commit()
            raise ValueError("Código expirado. Solicite um novo código.")

        if login_code.attempts >= self.MAX_CODE_ATTEMPTS:
            login_code.used_at = now

            self.auth_events.create(
                event_type="CODE_ATTEMPTS_EXCEEDED",
                phone=phone,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.commit()
            raise ValueError("Muitas tentativas. Solicite um novo código.")

        login_code.attempts += 1

        if not verify_code_hash(code, login_code.code_hash):
            self.auth_events.create(
                event_type="CODE_INVALID",
                phone=phone,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.commit()
            raise ValueError("Código inválido.")

        login_code.used_at = now

        user = self.users.get_by_phone(phone)

        if user is None:
            user = self.users.create(phone=phone)

            self.auth_events.create(
                event_type="USER_CREATED",
                phone=phone,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        access_token = create_access_token(str(user.id))

        self.auth_events.create(
            event_type="CODE_VERIFIED",
            phone=phone,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.commit()

        return user, access_token