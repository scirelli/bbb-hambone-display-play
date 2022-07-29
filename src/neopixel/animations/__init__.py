from typing import Tuple

from .Animator import Animator, FailAnimator, NotAnAnimator, NullAnimator
from .ball.bounce import BounceMultiple, BounceSimple
from .fades.rainbow import Rainbow, RainbowB
from .fades.strip import StripFadeTest
from .Point import Point

__all__: Tuple[str, ...] = (
    "Animator",
    "NullAnimator",
    "FailAnimator",
    "NotAnAnimator",
    "Point",
    "Rainbow",
    "RainbowB",
    "BounceSimple",
    "BounceMultiple",
    "StripFadeTest",
)
