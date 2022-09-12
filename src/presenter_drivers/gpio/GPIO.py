from __future__ import annotations

from abc import ABC, abstractmethod


class GPIO(ABC):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass

    @abstractmethod
    def input(self) -> int:
        pass

    @abstractmethod
    def output(self) -> None:
        pass
