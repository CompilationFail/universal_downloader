import sys

from . import download

if __name__ == "__main__":
    url = sys.argv[1]
    title = sys.argv[2]
    download(url, title)
