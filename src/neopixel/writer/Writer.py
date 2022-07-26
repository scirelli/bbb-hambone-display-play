from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type


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
    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> None:
        pass
