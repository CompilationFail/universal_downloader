from typing import Any, Callable, List


class DownloaderInvoker:
    def __init__(self, checker: Callable[[str], bool], constructor: Callable[[], Any]):
        self.checker = checker
        self.contructor = constructor

    def try_construct(self, url: str):
        if self.checker(url):
            return self.contructor()


class DownloaderRegistry:
    def __init__(self):
        self.downloaders: List[DownloaderInvoker] = []

    def register(self, downloader: DownloaderInvoker):
        self.downloaders.append(downloader)

    def try_construct(self, url: str):
        for downloader in self.downloaders:
            result = downloader.try_construct(url)
            if result is not None:
                return result
        return None
