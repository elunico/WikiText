from typing import Protocol, List


class Writeable(Protocol):
    def __init__(self, string: str):
        pass

    def write(self, string: str) -> None:
        pass

    def writelines(self, lines: List[str]) -> None:
        pass

    def close(self) -> None:
        pass


class StringFile:
    def __init__(self, string):
        self.string = string

    def write(self, string):
        self.string += string

    def writelines(self, lines):
        self.write('\n'.join(lines))

    def close(self):
        pass
