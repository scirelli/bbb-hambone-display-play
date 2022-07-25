from __future__ import annotations

from sys import stdout

from .Writer import Writer


class STDOutWriter(Writer):
    def write(self, b: bytearray) -> None:
        stdout.write(b.decode())

    def __enter__(self) -> Writer:
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        pass

    def __del__(self) -> None:
        pass
