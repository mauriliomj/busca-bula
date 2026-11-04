import hashlib
import hmac

from app.core.settings import get_settings


def build_catalog_writer_role_name() -> str:
    return f"{get_settings().catalog_database_name}_writer"


def build_catalog_reader_role_name() -> str:
    return f"{get_settings().catalog_database_name}_reader"


def derive_catalog_role_password(role_name: str) -> str:
    secret = get_settings().tenant_database_secret.encode()
    return hmac.new(secret, f"catalog:{role_name}".encode(), hashlib.sha256).hexdigest()
