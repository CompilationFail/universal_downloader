import asyncio
import os
from typing import Any, Dict

import requests

PROXY_ADDRESS = "http://127.0.0.1:7890"
HEADERS = None
COOKIES = None
SESSION = None
USE_PROXY = False


def get_session() -> requests.Session:
    global SESSION
    if SESSION is None:
        SESSION = requests.session()
    return SESSION


def set_proxy(use: bool):
    global USE_PROXY
    USE_PROXY = use


def set_cookies(cookies):
    global COOKIES
    COOKIES = cookies


def set_headers(headers):
    global HEADERS
    HEADERS = headers


def update_headers(key, value):
    global HEADERS
    if HEADERS is None:
        HEADERS = {}
    HEADERS[key] = value


MAX_CONCURRENCY = -1
ASYNC_SEMA = None


def set_async_http_max_concurrency(max_concurrence: int):
    global ASYNC_SEMA, MAX_CONCURRENCY
    if MAX_CONCURRENCY != max_concurrence:
        MAX_CONCURRENCY = max_concurrence
        ASYNC_SEMA = asyncio.Semaphore(max_concurrence)


def get_current_connections():
    if ASYNC_SEMA is None:
        return -1
    return MAX_CONCURRENCY - ASYNC_SEMA._value


def build_args(**kwargs) -> Dict[str, Any]:
    if USE_PROXY:
        kwargs["proxies"] = {
            "http_proxy": PROXY_ADDRESS,
            "https_proxy": PROXY_ADDRESS,
        }
    if COOKIES is not None and "cookies" not in kwargs:
        kwargs["cookies"] = COOKIES
    if HEADERS is not None:
        headers = HEADERS
        headers.update(kwargs.get("headers", {}))
        kwargs["headers"] = HEADERS
    return kwargs


async def http_get(url: str, **kwargs) -> requests.Response:
    args = build_args(**kwargs)
    session = get_session()
    if ASYNC_SEMA is not None:
        async with ASYNC_SEMA:
            resp = session.get(url, **args)
    else:
        resp = session.get(url, **args)
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
    session = get_session()
    args = build_args(
        stream=True,
        headers={"Range": f"bytes={current_size}-"} if current_size > 0 else {},
        timeout=10,
    )

    try:
        resp: requests.Response = session.get(url, **args)
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
