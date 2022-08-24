from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from tabulate import tabulate


class Stater(ABC):
    @abstractmethod
    def get_headers(self) -> Sequence[str]:
        return []

    @abstractmethod
    def get_row(self) -> Sequence[str]:
        return ""


class AsTableStr(Stater):
    def __str__(self) -> str:
        return tabulate(list(self.get_row()), headers=self.get_headers())
