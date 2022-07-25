from __future__ import annotations

from abc import ABC, abstractmethod


class Writer(ABC):
    @abstractmethod
    def write(self, b: bytearray) -> None:
        """
        Abstract write method, write color data to chosen location.
        """

    @abstractmethod
    def __enter__(self) -> Writer:
        pass

    @abstractmethod
    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        pass
