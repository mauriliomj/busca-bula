from fastapi import Request

from app.core.logo_validation import MAXIMUM_LOGO_SIZE_IN_BYTES, LogoUpload, normalize_content_type
from app.exceptions.domain_exceptions import LogoTooLargeError


async def read_logo_upload(request: Request) -> LogoUpload:
    content = bytearray()
    async for chunk in request.stream():
        content.extend(chunk)
        if len(content) > MAXIMUM_LOGO_SIZE_IN_BYTES:
            raise LogoTooLargeError()
    return LogoUpload(bytes(content), normalize_content_type(request.headers.get("content-type")))
