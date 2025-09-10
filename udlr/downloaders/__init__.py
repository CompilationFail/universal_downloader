from udlr.schema import DownloaderRegistry

from . import u9mm, zhxs

modules = [u9mm, zhxs]


def register(registry: DownloaderRegistry):
    for module_name in modules:
        module_name.register(registry)
