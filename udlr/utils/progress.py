from typing import Optional


class Progress:
    def __init__(
        self, total: int, current: int = 0, msg: str = "", has_fail: bool = False
    ):
        self.total = total
        self.current = current
        self.msg = msg
        if has_fail:
            self.fail = 0
        self.print()

    def incr(self, success=True):
        self.current += 1
        if not success:
            assert hasattr(self, "fail")
            self.fail += 1
        self.print()

    def update_progress(self, current: int, fail: Optional[int] = None):
        self.current = current
        if fail is not None:
            assert hasattr(self, "fail")
            self.fail = fail
        self.print()

    def print(self):
        total = str(self.total)
        current = str(self.current)
        if len(current) < len(total):
            current = " " * (len(total) - len(current)) + current
        msg = f"{self.msg} [{current}/{total}]"
        if hasattr(self, "fail") and self.fail > 0:
            msg += "  fails: " + str(self.fail)
        print(msg, end="\r")
