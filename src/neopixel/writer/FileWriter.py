from __future__ import annotations

from tempfile import NamedTemporaryFile
from typing import BinaryIO, ClassVar

from .Writer import Writer


class FileWriter(Writer):
    FILE_SUFFIX: ClassVar[str] = ".bin"

    def __init__(self, file_path: str = ""):
        self.file: BinaryIO = None

        if file_path == "":
            self.file = NamedTemporaryFile("ab", 0, suffix=FileWriter.FILE_SUFFIX, delete=False)
        else:
            self.file = open(file_path, "ab", 0)  # pylint: disable=consider-using-with

    def write(self, b: bytearray) -> None:
        self.file.write(b)

    def __enter__(self) -> Writer:
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        if self.file:
            self.file.close()

    def __del__(self) -> None:
        if self.file:
            self.file.close()
