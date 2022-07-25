from dataclasses import dataclass

from neopixel.animations.Color import Color
from neopixel.animations.Point import Point


@dataclass
class Ball():
    position: Point = Point(0, 0)
    vel: Point = Point()
    color: Color = Color()
    elasticity: float = 1
