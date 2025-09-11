import asyncio
import contextvars
import os
from dataclasses import dataclass, replace
from enum import Enum

import requests
import yaml


@dataclass
class Config:
    proxy_address: str = "http://127.0.0.1:7890"
    use_proxy: bool = True
    max_concurrency: int = 16

    @staticmethod
    def get_config_path() -> str:
        path = os.path.realpath(__file__)
        for _ in range(3):
            path = os.path.split(path)[0]
        path = os.path.join("config.yaml")
        return path


def load_config():
    path = Config.get_config_path()
    try:
        with open(path) as file:
            data = yaml.safe_load(file.read())
        assert isinstance(data, dict), "the loaded yaml file is not a valid config"
        return Config(**data)
    except Exception as e:
        print("Fail to load config:", e)
        return Config()


_GLOBAL_CONFIG: Config = load_config()
_SAVE_LOCK = asyncio.Lock()


async def save_config():
    async with _SAVE_LOCK:
        global _GLOBAL_CONFIG
        try:
            data = _GLOBAL_CONFIG.__dict__
            with open(Config.get_config_path(), "w") as file:
                yaml.dump(data, file)
        except Exception:
            print("Fail to save yaml")


class InvokeType(str, Enum):
    COMMANDLINE = "commandline"
    WEB = "web"


class Session(Config):
    def __init__(self, config: Config, invoke_type: InvokeType, **overrides):
        config = replace(config, **overrides)
        for k, v in config.__dict__.items():
            setattr(self, k, v)
        self.http_session = None
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.headers = None
        self.cookies = None

    def set_proxy(self, use: bool):
        self.use_proxy = use

    def set_cookies(self, cookies):
        self.cookies = cookies

    def set_headers(self, headers: dict):
        self.headers = headers

    def update_headers(self, **kwargs):
        if self.headers is None:
            self.headers = {}
        self.headers.update(kwargs)

    def get_http_session(self):
        if self.http_session is None:
            self.http_session = requests.Session()
        return self.http_session

    def set_async_http_max_concurrency(self, max_concurrence: int):
        if self.max_concurrency != max_concurrence:
            self.max_concurrency = max_concurrence
            self.semaphore = asyncio.Semaphore(max_concurrence)


def update_config(**overrides):
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = replace(_GLOBAL_CONFIG, **overrides)


_SESSION = contextvars.ContextVar(
    "SESSION", default=Session(_GLOBAL_CONFIG, InvokeType.COMMANDLINE)
)


def get_session() -> Session:
    return _SESSION.get()


def new_web_session(**overrides):
    _SESSION.set(Session(_GLOBAL_CONFIG, InvokeType.WEB, **overrides))


def new_commandline_session(**overrides):
    _SESSION.set(Session(_GLOBAL_CONFIG, InvokeType.COMMANDLINE, **overrides))
