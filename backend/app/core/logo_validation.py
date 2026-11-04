from dataclasses import dataclass

from app.exceptions.domain_exceptions import LogoTooLargeError, UnsupportedLogoError

MAXIMUM_LOGO_SIZE_IN_BYTES = 512 * 1024

SVG_CONTENT_TYPE = "image/svg+xml"


@dataclass(frozen=True)
class LogoUpload:
    content: bytes
    content_type: str


def has_png_signature(content: bytes) -> bool:
    return content.startswith(b"\x89PNG\r\n\x1a\n")


def has_jpeg_signature(content: bytes) -> bool:
    return content.startswith(b"\xff\xd8\xff")


def has_webp_signature(content: bytes) -> bool:
    return content[:4] == b"RIFF" and content[8:12] == b"WEBP"


def looks_like_svg(content: bytes) -> bool:
    return b"<svg" in content[:2048].lower()


SIGNATURE_CHECKS = {
    "image/png": has_png_signature,
    "image/jpeg": has_jpeg_signature,
    "image/webp": has_webp_signature,
    SVG_CONTENT_TYPE: looks_like_svg,
}


def normalize_content_type(content_type: str | None) -> str:
    return (content_type or "").split(";")[0].strip().lower()


def validate_logo(upload: LogoUpload) -> LogoUpload:
    if len(upload.content) > MAXIMUM_LOGO_SIZE_IN_BYTES:
        raise LogoTooLargeError()
    signature_check = SIGNATURE_CHECKS.get(upload.content_type)
    if signature_check is None or not upload.content or not signature_check(upload.content):
        raise UnsupportedLogoError()
    return upload
