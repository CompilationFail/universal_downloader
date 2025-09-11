# Universal Downloader

Downloading various types of media
- text:
  - novels
- image
  - mangas
- videos:
  - download directly from a m3u8 file
  - download from websites

## Supported Sites

novel sites:

```plain
https://m.u9mm.com
https://www.zhenhunxiaoshuo.com
```

manga sites:

```plain
```

## Usage

```bash
pip install git+https://github.com/CompilationFail/universal_downloader
python3 -m udlr [url] [title]
```

examples:
```bash
python3 -m udlr "https://m.u9mm.com/novel/list/96999/1.html" --title novel1 --no-proxy
python3 -m udlr "https://www.zhenhunxiaoshuo.com/woqinaidefayixiaojie/" --title novel2
```

## Developer Notes

```plain
.
├── udlr/
│   ├── __main__.py # entrypoint to commandline tool
│   ├── novel.py    # wrapper for novel downloader
│   ├──downloads/
│      └── downloaders, each implements functions needed
│              and return a downloader (using wrapper)
├── downloads/
│   └── downloaded content...
└── README.md
```

Use uv to manage dependencies

Initialize the environments

```bash
uv venv
uv run pip install
uv run pre-commit install
```

test:

```bash
uv run python3 -m udlr [url] [title]
```
