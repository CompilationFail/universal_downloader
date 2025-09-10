from udlr.schema import DownloaderRegistry

from . import u9mm

modules = [u9mm]


def register(registry: DownloaderRegistry):
    for module_name in modules:
        module_name.register(registry)
