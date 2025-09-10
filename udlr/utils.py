import asyncio
import hashlib
import os
from typing import Any, Dict

import requests

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

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


ASYNC_SEMA = None


def set_async_http_max_concurrency(max_concurrence: int):
    global ASYNC_SEMA
    ASYNC_SEMA = asyncio.Semaphore(max_concurrence)


async def http_get(url: str) -> requests.Response:
    session = get_session()
    args: Dict[str, Any] = {"url": url}
    if USE_PROXY:
        args["proxies"] = proxies
    if COOKIES is not None:
        args["cookies"] = COOKIES
    if HEADERS is not None:
        args["HEADERS"] = HEADERS
    if ASYNC_SEMA is not None:
        async with ASYNC_SEMA:
            resp = session.get(**args)
    else:
        resp = session.get(**args)
    return resp


async def http_get_decode(url, encoding="utf-8") -> str:
    content = (await http_get(url)).content
    assert isinstance(content, bytes)
    text = content.decode(encoding=encoding)
    return text


PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]


def hash(s: str | bytes):
    if isinstance(s, str):
        s = s.encode()
    return hashlib.sha256(s).hexdigest()


def abs_path(*args):
    path = PATH
    for i in args:
        path = os.path.join(path, i)
    return path


def find(
    text: str,
    begin: str,
    end: str,
    start: int = 0,
    offset: int = 0,
    remove_boundary: bool = True,
    strip: bool = True,
):
    left = text.find(begin, start)
    if offset == 0:
        offset = len(begin)
    right = text.find(end, left + offset)
    text = text[left:right]
    if remove_boundary:
        text = text[len(begin) :]
    if strip:
        text = text.strip()
    return text, right
