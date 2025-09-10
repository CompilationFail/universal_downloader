from typing import List

from udlr.novel import Chapter, NovelDownloader
from udlr.schema import DownloaderInvoker, DownloaderRegistry
from udlr.utils import find, http_get_decode

base_url = "https://www.zhenhunxiaoshuo.com"
test_menu_url = "/woqinaidefayixiaojie/"


async def get_chapters(url: str, title: str) -> List[Chapter]:
    text = await http_get_decode(url)
    text, _ = find(text, '<div class="excerpts">', "</div>")
    pos = 0
    lis: List[Chapter] = []
    while True:
        pos = text.find('class="excerpt excerpt-c3"', pos + 1)
        if pos == -1:
            break
        chapter_title, pos = find(text, '<a title="', '"', pos + 1)
        chapter_url, pos = find(text, 'href="', '"', pos + 1)
        lis.append(Chapter.construct(chapter_url, title=chapter_title))
    return lis


async def download_chapter(url: str, title: str, chap: Chapter):
    chapter_title = chap.get_title()
    url = chap.url
    text = await http_get_decode(url)
    content, _ = find(text, '<article class="article-content">', "</article>")
    content = "<h1>" + chapter_title + "</h1>" + content
    chap.content = content


def get_downloader():
    return NovelDownloader(get_chapters, download_chapter)


def register(registry: DownloaderRegistry):
    registry.register(
        DownloaderInvoker(lambda s: s.find("zhenhunxiaoshuo.com") != -1, get_downloader)
    )
