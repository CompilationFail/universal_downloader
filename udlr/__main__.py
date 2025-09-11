import argparse
import asyncio

from .registry import get_registry
from .utils import get_session
from .utils.context import save_config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Univeral Downloader", description="download any media you want", epilog=""
    )
    parser.add_argument("url")  # positional argument
    parser.add_argument("-t", "--title")  # option that takes a value
    parser.add_argument("--proxy", action=argparse.BooleanOptionalAction)
    parser.add_argument("-s", "--save-config", action="store_true", default=False)
    args = parser.parse_args()
    url = args.url
    args_dict = args.__dict__
    args_dict.pop("url")
    proxy = args_dict.get("proxy", None)
    if proxy is not None:
        print("setting proxy", proxy)
        get_session().set_proxy(proxy)

    registry = get_registry()
    downloader = registry.try_construct(url)
    if downloader is None:
        print("No matching downloader")
    else:
        downloader.download(url, **args_dict)

    if args.save_config:
        asyncio.run(save_config())
