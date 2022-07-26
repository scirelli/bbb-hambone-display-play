from typing import Tuple

from .Animator import Animator, FailAnimator, NotAnAnimator, NullAnimator
from .fades.rainbow import Rainbow, RainbowB
from .Point import Point

__all__: Tuple[str, ...] = (
    "Animator",
    "NullAnimator",
    "FailAnimator",
    "NotAnAnimator",
    "Point",
    "Rainbow",
    "RainbowB",
)
