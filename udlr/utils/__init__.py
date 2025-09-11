import hashlib
import os

PATH = os.path.split(os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])[0]


def hash(s: str | bytes):
    if isinstance(s, str):
        s = s.encode()
    return hashlib.sha256(s).hexdigest()


def abs_path(*args):
    path = PATH
    for i in args:
        path = os.path.join(path, i)
    return path


def find(
    text: str,
    begin: str,
    end: str,
    start: int = 0,
    offset: int = 0,
    remove_boundary: bool = True,
    strip: bool = True,
):
    left = text.find(begin, start)
    if offset == 0:
        offset = len(begin)
    right = text.find(end, left + offset)
    text = text[left:right]
    if remove_boundary:
        text = text[len(begin) :]
    if strip:
        text = text.strip()
    return text, right
