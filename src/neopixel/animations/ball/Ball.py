from dataclasses import dataclass

from neopixel.animations.Point import Point
from neopixel.display import Color


@dataclass
class Ball:
    position: Point = Point()
    vel: Point = Point()
    color: Color = Color()
    elasticity: float = 1
