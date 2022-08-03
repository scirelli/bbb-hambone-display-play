from __future__ import annotations

from tempfile import NamedTemporaryFile
from types import TracebackType
from typing import IO, ClassVar, Optional, Type

from .Writer import Writer


class FileWriter(Writer):
    FILE_SUFFIX: ClassVar[str] = ".bin"

    def __init__(self, file_path: str = ""):
        self.file: IO[bytes]
        if file_path == "":
            self.file = NamedTemporaryFile(
                "ab", 0, suffix=FileWriter.FILE_SUFFIX, delete=False
            )
        else:
            self.file = open(file_path, "ab", 0)

    def write(self, b: bytearray) -> None:
        self.file.write(b)

    def __enter__(self) -> Writer:
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> None:
        self.file.close()

    def __del__(self) -> None:
        if self.file:
            self.file.close()
