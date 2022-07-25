from time import time

from ..Animator import Animator
from ..Color import Color
from .Ball import Ball


class BounceAnimation(Animator):
    def __init__(self, screen: list[Color]):
        self.ball: Ball = Ball()
        self.screen: list[Color] = screen

    def animate(self, elapsedTime: float):
        print(elapsedTime)
