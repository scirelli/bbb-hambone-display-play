from dataclasses import dataclass
from math import floor
from typing import ClassVar


@dataclass
class Color:
    MIN_COLOR: ClassVar[float] = 0.0
    MAX_COLOR: ClassVar[float] = 255.0

    r: float = 0.0
    g: float = 0.0
    b: float = 0.0

    def __str__(self) -> str:
        return f"{floor(self.r)} {floor(self.g)} {floor(self.b)}"


def HSVtoRGB(h: float, s: float, v: float) -> dict[str, int]:
    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    i: float = 0.0
    f: float = 0.0
    p: float = 0.0
    q: float = 0.0
    t: float = 0.0

    i = floor(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    match i % 6:
        case 0:
            r = v
            g = t
            b = p
        case 1:
            r = q
            g = v
            b = p
        case 2:
            r = p
            g = v
            b = t
        case 3:
            r = p
            g = q
            b = v
        case 4:
            r = t
            g = p
            b = v
        case 5:
            r = v
            g = p
            b = q

    return {"r": round(r * 255), "g": round(g * 255), "b": round(b * 255)}


def RED(color: int) -> int:
    return (color & 0x0000FF00) >> 8


def GREEN(color: int) -> int:
    return (color & 0x00FF0000) >> 16


def BLUE(color: int) -> int:
    return (color & 0x000000FF) >> 0
