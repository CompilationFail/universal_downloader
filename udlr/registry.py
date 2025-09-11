from . import downloaders
from .schema import DownloaderRegistry


def register(registry: DownloaderRegistry):
    downloaders.register(registry)


REGISTRY = None


def get_registry() -> DownloaderRegistry:
    global REGISTRY
    if REGISTRY is None:
        REGISTRY = DownloaderRegistry()
        register(REGISTRY)
    return REGISTRY
