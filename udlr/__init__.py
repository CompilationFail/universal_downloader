from . import downloaders
from .schema import DownloaderRegistry
from .utils.http import set_async_http_max_concurrency, set_proxy


def register(registry: DownloaderRegistry):
    downloaders.register(registry)


def download(url, title):
    set_proxy(True)
    set_async_http_max_concurrency(16)
    registry = DownloaderRegistry()
    register(registry)
    downloader = registry.try_construct(url)
    if downloader is None:
        print("No matching downloader")
    else:
        downloader.download(url, title)
