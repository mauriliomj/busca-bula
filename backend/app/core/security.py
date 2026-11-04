import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.settings import get_settings
from app.exceptions.domain_exceptions import InvalidAccessTokenError

PLATFORM_SCOPE = "platform"

password_hasher = PasswordHash.recommended()


@dataclass(frozen=True)
class AccessTokenPayload:
    subject_id: int
    scope: str
    role: str


def build_tenant_scope(slug: str) -> str:
    return f"tenant:{slug}"


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def derive_signing_key(scope: str) -> str:
    secret = get_settings().jwt_secret.encode()
    return hmac.new(secret, scope.encode(), hashlib.sha256).hexdigest()


def create_access_token(subject_id: int, scope: str, role: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(subject_id), "scope": scope, "role": role, "exp": expires_at}
    return jwt.encode(payload, derive_signing_key(scope), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, expected_scope: str) -> AccessTokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            derive_signing_key(expected_scope),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "scope", "role", "exp"]},
        )
    except jwt.PyJWTError as error:
        raise InvalidAccessTokenError() from error
    if payload["scope"] != expected_scope:
        raise InvalidAccessTokenError()
    return AccessTokenPayload(int(payload["sub"]), payload["scope"], payload["role"])
