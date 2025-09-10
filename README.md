# Universal Downloader

## Supported Sites

novel sites:

```plain
https://m.u9mm.com
https://www.zhenhunxiaoshuo.com'
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
python3 -m udlr "https://m.u9mm.com/novel/list/96999/1.html" novel1
python3 -m udlr "https://www.zhenhunxiaoshuo.com/woqinaidefayixiaojie/" novel2
```

## Developer Notes

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
