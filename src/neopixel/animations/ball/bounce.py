from neopixel.display import Display

from ..Animator import Animator
from .Ball import Ball


class BounceAnimation(Animator):
    def __init__(self, display: Display):
        self._ball: Ball = Ball()
        self._screen = display

    def animate(self) -> None:
        pass
