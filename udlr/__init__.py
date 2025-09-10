from . import downloaders
from .schema import DownloaderRegistry
from .utils import set_proxy

set_proxy(True)


def register(registry: DownloaderRegistry):
    downloaders.register(registry)


def download(url, title):
    registry = DownloaderRegistry()
    register(registry)
    downloader = registry.try_construct(url)
    if downloader is None:
        print("No matching downloader")
    else:
        downloader.download(url, title)
