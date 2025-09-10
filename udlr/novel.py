import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

from ebooklib import epub
from pathvalidate import sanitize_filename

from .utils import abs_path, hash


@dataclass
class Chapter:
    url: str
    path: str
    title: Optional[str] = None
    content: Optional[str] = None

    @classmethod
    def construct(cls, url, **kwargs):
        path = hash(url)
        return cls(url, path, **kwargs)

    def check_complete(self) -> bool:
        return self.title is not None and self.content is not None

    def load(self, directory) -> bool:
        path = os.path.join(directory, self.path)
        if self.check_complete():
            return True
        if not os.path.exists(path):
            return False
        try:
            with open(path) as file:
                data = json.loads(file.read())
                self.title = data["title"]
                self.content = data["content"]
            return True
        except Exception as e:
            print(f"Fail to read json({self.path}): ", e)
            return False

    def save(self, directory):
        path = os.path.join(directory, self.path)
        data = {
            "title": self.title,
            "content": self.content,
        }
        with open(path, "w") as file:
            json.dump(data, file)

    def get_title(self) -> str:
        assert self.title is not None, "Missing chapter title"
        return self.title

    def get_content(self) -> str:
        assert self.content is not None, "Missing content"
        return self.content


class NovelDownloader:
    def __init__(
        self,
        get_chapter_fn: Callable[[str, str], list[Chapter]],
        download_chapter_fn: Callable[[str, str, Chapter], None],
    ):
        self.get_chapters = get_chapter_fn
        self.download_chapter = download_chapter_fn

    async def _download_chapter(self, data: Chapter):
        data_path = os.path.join(self.base_path, "data")
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        if data.load(data_path):
            return
        try:
            async with self.sema:
                self.download_chapter(self.url, self.title, data)
            data.save(data_path)
            self.update_counter(True)
        except Exception as e:
            self.update_counter(False)
            print("Fail to download chapter:", e)

    async def _download(self):
        self.sema = asyncio.Semaphore(8)
        self.chapters = self.get_chapters(self.url, self.title)
        self.init_counter()
        await asyncio.gather(*[self._download_chapter(data) for data in self.chapters])

    def init_counter(self):
        self.counter = 0
        self.fail_count = 0
        print(
            "Downloading chapters: [%3d/%3d], fails: %3d"
            % (self.counter, len(self.chapters), self.fail_count),
            end="\r",
        )

    def update_counter(self, success: bool):
        self.counter += 1
        if not success:
            self.fail_count += 1
        print(
            "Downloading chapters: [%3d/%3d], fails: %3d"
            % (self.counter, len(self.chapters), self.fail_count),
            end="\r",
        )

    def _export(self):
        book = epub.EpubBook()
        # set metadata
        # book.set_identifier("hongsirong")
        book.set_title(self.title)
        book.set_language("zh")
        book.add_metadata("source", "url", self.url)

        toc = []
        spine: List[Any] = ["nav"]
        for idx, chapter in enumerate(self.chapters):
            html_name = f"{idx}.html"
            c1 = epub.EpubHtml(
                title=chapter.get_title(),
                file_name=html_name,
                lang="zh",
                content=chapter.content,
            )
            c1.content = chapter.get_content()
            book.add_item(c1)
            toc.append(epub.Link(html_name, chapter.title, str(idx)))
            spine.append(c1)

        # define Table Of Contents
        book.toc = toc
        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        # define CSS style
        style = "BODY {color: white;}"
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style,
        )
        # add CSS file
        book.add_item(nav_css)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = spine

        path = os.path.join(self.base_path, sanitize_filename(self.title + ".epub"))
        print("Saving to", path)
        epub.write_epub(path, book, {})

    def download(self, url, title):
        self.url = url
        self.title = title
        self.base_path = abs_path("downloads", sanitize_filename(title))
        asyncio.run(self._download())
        self._export()
