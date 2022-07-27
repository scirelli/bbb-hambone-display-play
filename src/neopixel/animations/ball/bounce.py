from typing import Any

from neopixel.animations.Point import Point
from neopixel.display import Color, NullDisplay

from ..Animator import Animator
from .Ball import Ball

NANO_SEC_IN_SEC = 1_000_000_000
SEC_IN_NANO_SEC = 1 / NANO_SEC_IN_SEC
COLOR_MAX = 255


class BounceSimple(Animator):
    """
    Simple bouncing "ball" animation.
    """

    GRAVITY: float = -9.81  # -9.81 m / 1 s^2

    def __init__(self, config: dict[str, Any]):
        self._screen: list[Color] = config.get("display", NullDisplay()).get_display()
        self._ground: Point = Point(0, len(self._screen))
        self._ball: Ball = Ball(color=Color(0, 0, 0x0F))
        self._acc: float = -1 * BounceSimple.GRAVITY

    def animate(self, dt_ns: int) -> None:
        self._screen[int(self._ball.position.y)].r = self._screen[
            int(self._ball.position.y)
        ].g = self._screen[int(self._ball.position.y)].b = 0

        dt_s = dt_ns * SEC_IN_NANO_SEC
        # s(t) = s0 + v0*t + 1/2 * a * t^2
        self._ball.vel.y = self._ball.vel.y + (0.5 * self._acc * dt_s)
        self._ball.position.y = self._ball.position.y + (self._ball.vel.y * dt_s)
        if self._ball.position.y >= self._ground.y:
            self._ball.position.y = self._ground.y - 1
            self._ball.vel.y = -self._ball.vel.y * self._ball.elasticity
        elif self._ball.position.y < 0:
            self._ball.position.y = 0
            self._ball.vel.y = -self._ball.vel.y * self._ball.elasticity

        self._screen[int(self._ball.position.y)].r = self._ball.color.r
        self._screen[int(self._ball.position.y)].g = self._ball.color.g
        self._screen[int(self._ball.position.y)].b = self._ball.color.b
