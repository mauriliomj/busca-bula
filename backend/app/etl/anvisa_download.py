import os
import ssl
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import httpx

from app.core.settings import get_settings

DOWNLOAD_CHUNK_SIZE = 1024 * 1024


def build_legacy_tls_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    context.set_ciphers("DEFAULT@SECLEVEL=1")
    return context


class AnvisaFileDownloader:
    def __init__(self, cache_directory: Path | None = None) -> None:
        self.cache_directory = cache_directory or Path(get_settings().catalog_cache_dir)

    def download(self, url: str, file_name: str) -> Path:
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        destination = self.cache_directory / file_name
        headers = self.build_request_headers(destination)
        timeout = httpx.Timeout(60, read=300)
        with httpx.Client(verify=build_legacy_tls_context(), timeout=timeout, follow_redirects=True) as client:
            with client.stream("GET", url, headers=headers) as response:
                if response.status_code == httpx.codes.NOT_MODIFIED:
                    return destination
                response.raise_for_status()
                self.save_response(response, destination)
        return destination

    def build_request_headers(self, destination: Path) -> dict[str, str]:
        headers = {"User-Agent": get_settings().catalog_user_agent}
        if destination.exists():
            headers["If-Modified-Since"] = formatdate(destination.stat().st_mtime, usegmt=True)
        return headers

    def save_response(self, response: httpx.Response, destination: Path) -> None:
        partial_file = destination.with_name(f"{destination.name}.partial")
        with partial_file.open("wb") as output:
            for chunk in response.iter_bytes(DOWNLOAD_CHUNK_SIZE):
                output.write(chunk)
        partial_file.replace(destination)
        last_modified = response.headers.get("Last-Modified")
        if last_modified:
            timestamp = parsedate_to_datetime(last_modified).timestamp()
            os.utime(destination, (timestamp, timestamp))
