from __future__ import annotations

from sys import stdout
from types import TracebackType
from typing import Optional, Type

from .Writer import Writer


class STDOutWriter(Writer):
    def write(self, b: bytearray) -> None:
        stdout.write(b.decode())

    def __enter__(self) -> Writer:
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> None:
        pass

    def __del__(self) -> None:
        pass
