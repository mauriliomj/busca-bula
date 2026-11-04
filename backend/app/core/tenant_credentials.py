import hashlib
import hmac

from app.core.settings import get_settings


def build_tenant_database_name(slug: str) -> str:
    return f"{get_settings().tenant_database_prefix}{slug.replace('-', '_')}"


def build_tenant_role_name(slug: str) -> str:
    return build_tenant_database_name(slug)


def derive_tenant_password(slug: str) -> str:
    secret = get_settings().tenant_database_secret.encode()
    return hmac.new(secret, slug.encode(), hashlib.sha256).hexdigest()
