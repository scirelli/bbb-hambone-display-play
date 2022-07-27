from dataclasses import dataclass
from typing import Any

from neopixel.animations.Point import Point
from neopixel.display import Color


@dataclass
class Ball:
    position: Point = Point()
    vel: Point = Point()
    color: Color = Color()
    elasticity: float = 1


def createBall(config: dict[str, Any]) -> Ball:
    vel = Point(
        float(config.get("vel", {}).get("x", 0)),
        float(config.get("vel", {}).get("y", 0)),
    )
    pos = Point(
        float(config.get("position", {}).get("x", 0)),
        float(config.get("position", {}).get("y", 0)),
    )
    col = Color(
        float(config.get("color", {}).get("r", 0)),
        float(config.get("color", {}).get("g", 0)),
        float(config.get("color", {}).get("b", 0)),
    )
    ela = float(config.get("elasticity", 1))

    return Ball(
        position=pos,
        vel=vel,
        color=col,
        elasticity=ela,
    )
