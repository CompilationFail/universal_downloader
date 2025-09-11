from typing import Any, Callable, List


class DownloaderInvoker:
    def __init__(
        self, checker: Callable[[str], bool], constructor: Callable[[], Any], msg
    ):
        self.checker = checker
        self.contructor = constructor
        self.msg = msg

    def check(self, url: str):
        return self.checker(url)

    def try_construct(self, url: str):
        if self.checker(url):
            return self.contructor()


class DownloaderRegistry:
    def __init__(self):
        self.downloaders: List[DownloaderInvoker] = []

    def register(self, downloader: DownloaderInvoker):
        self.downloaders.append(downloader)

    def get_downloader_msg(self, url: str):
        for downloader in self.downloaders:
            if downloader.check(url):
                return downloader.msg
        return None

    def try_construct(self, url: str):
        for downloader in self.downloaders:
            result = downloader.try_construct(url)
            if result is not None:
                return result
        return None
