import os
from typing import Any, Dict

import requests

from .context import get_session


def build_args(**kwargs) -> Dict[str, Any]:
    session = get_session()
    if session.use_proxy:
        kwargs["proxies"] = {
            "http_proxy": session.proxy_address,
            "https_proxy": session.proxy_address,
        }
    if session.cookies is not None and "cookies" not in kwargs:
        kwargs["cookies"] = session.cookies
    if session.headers is not None:
        headers = session.headers
        headers.update(kwargs.get("headers", {}))
        kwargs["headers"] = session.headers
    return kwargs


async def http_get(url: str, **kwargs) -> requests.Response:
    args = build_args(**kwargs)
    session = get_session()
    http_session = session.get_http_session()
    async with session.semaphore:
        resp = http_session.get(url, **args)
    return resp


async def http_get_decode(url, encoding="utf-8") -> str:
    content = (await http_get(url)).content
    assert isinstance(content, bytes)
    text = content.decode(encoding=encoding)
    return text


CHUNK_SIZE = 8192  # 8 KiB


def http_get_file(url, file_path) -> bool:
    # Check if the file already exists to resume download
    if os.path.exists(file_path):
        current_size = os.path.getsize(file_path)
    else:
        current_size = 0
    http_session = get_session().get_http_session()
    args = build_args(
        stream=True,
        headers={"Range": f"bytes={current_size}-"} if current_size > 0 else {},
        timeout=10,
    )
    try:
        resp: requests.Response = http_session.get(url, **args)
        resp.raise_for_status()  # Check for HTTP errors

        # Determine total size from headers
        # total_size = int(resp.headers.get("content-length", 0)) + current_size

        # Check if download is already complete
        if resp.status_code == 206:  # Partial content
            mode = "ab"  # Append mode
        elif resp.status_code == 200:  # Full content
            mode = "wb"  # Overwrite mode
            current_size = 0  # Reset since we're downloading from start
        else:
            raise Exception(f"Unexpected status code: {resp.status_code}")

        # Download the file in chunks
        with open(file_path, mode) as file:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    if isinstance(chunk, str):
                        chunk = chunk.encode("utf-8")
                    file.write(chunk)
                    current_size += len(chunk)
        return True
    except Exception as e:
        print("Download fail:", e)
        return False
