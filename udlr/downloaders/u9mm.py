from typing import List

from udlr.novel import Chapter, NovelDownloader
from udlr.schema import DownloaderInvoker, DownloaderRegistry
from udlr.utils import find, http_get

base_url = "https://m.u9mm.com"
test_menu_url = "https://m.u9mm.com/novel/list/96999/1.html"  # 红丝绒


def force_decode(content) -> str:
    assert isinstance(content, bytes)
    text = content.decode("utf-8")
    return text


def get_chapters(url: str, title: str) -> List[Chapter]:
    text = force_decode(http_get(url).content)
    pos = 0
    lis: List[Chapter] = []
    while True:
        pos = text.find("<li><", pos + 1)
        if pos == -1:
            break
        chapter_url, pos = find(text, 'href="', '"', pos + 1)
        chapter_title, pos = find(text, ">", "<", pos + 1)
        lis.append(Chapter.construct(base_url + chapter_url, title=chapter_title))
    return lis


def download_chapter(url: str, title: str, chap: Chapter):
    title = chap.get_title()
    url = chap.url
    text = force_decode(http_get(url).content)
    left = text.find('<div id="nr1"')
    left = text.find(">", left + 1) + 1
    right = text.find("</div>", left + 1)
    content = "<h1>" + title + "</h1>" + text[left:right]
    chap.content = content


def get_downloader():
    return NovelDownloader(get_chapters, download_chapter)


def register(registry: DownloaderRegistry):
    registry.register(DownloaderInvoker(lambda s: s.find("u9mm") != -1, get_downloader))
