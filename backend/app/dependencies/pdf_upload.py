from fastapi import Request

from app.exceptions.domain_exceptions import InvalidLeafletPdfError, LeafletPdfTooLargeError

MAXIMUM_LEAFLET_PDF_SIZE_IN_BYTES = 15 * 1024 * 1024
PDF_SIGNATURE = b"%PDF-"


async def read_leaflet_pdf_upload(request: Request) -> bytes:
    content = bytearray()
    async for chunk in request.stream():
        content.extend(chunk)
        if len(content) > MAXIMUM_LEAFLET_PDF_SIZE_IN_BYTES:
            raise LeafletPdfTooLargeError()
    if not content.startswith(PDF_SIGNATURE):
        raise InvalidLeafletPdfError()
    return bytes(content)
