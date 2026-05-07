import hashlib
import hmac
import re
import secrets

from backend.core.config import settings
# Normaliza telefones enviados nas requisições
def normalize_phone_br(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("55") and len(digits) in [12, 13]:
        return digits
    if len(digits) in [10, 11]:
        return f"55{digits}"
    raise ValueError("Telefone inválido.")
# Geração de código de login(6 digítos)
def generate_login_code() -> str:
    return str(secrets.randbelow(900000) + 100000)
# Geração de HASH do código de login
def hash_code(code: str) -> str:
    return hmac.new(key=settings.JWT_SECRET_KEY.encode("utf-8"), msg=code.encode("utf-8"), digestmod=hashlib.sha256,).hexdigest()
# Verifica se o código de login bate com o armazenado no DATABASE
def verify_code_hash(code: str, code_hash: str) -> bool:
    candidate_hash = hash_code(code)
    return hmac.compare_digest(candidate_hash, code_hash)