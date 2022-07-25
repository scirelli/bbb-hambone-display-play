from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import chain
from typing import ClassVar

from neopixel.writer.Writer import Writer


@dataclass
class Color:
    MIN_COLOR: ClassVar[float] = 0.0
    MAX_COLOR: ClassVar[float] = 255.0
    """
    Color values should be from [0, 1]
    """
    r: float = 0
    g: float = 0
    b: float = 0


@dataclass
class Pixel():
    r: int = 0
    g: int = 0
    b: int = 0


class Display(ABC):
    @abstractmethod
    def get_display(self) -> list[Color]:
        pass


class Clearer(ABC):
    @abstractmethod
    def clear(self) -> None:
        pass


class DisplayClearer(Display, Clearer):
    pass


class DisplayDrawer(ABC):
    @abstractmethod
    def draw(self, display: Display) -> None:
        pass


class NeoPixelDisplay(DisplayDrawer, DisplayClearer):
    def __init__(self, length: int, writer: Writer):
        self.pixels: list[Color] = [Color()] * length
        self._writer = writer

    def clear(self):
        for pixel in range(self.pixels):
            pixel.r = pixel.g = pixel.b = 0.0

    def get_display(self) -> list[Color]:
        return self.pixels

    def draw(self, display: Display = None) -> None:
        out = []
        # self._writer.write(bytearray(chain.from_iterable([[int(x.r), int(x.g), int(x.b)] for x in self.get_display()])))
        for c in self.get_display():
            out.extend([int(c.r), int(c.g), int(c.b)])
        self._writer.write(bytearray(out))
