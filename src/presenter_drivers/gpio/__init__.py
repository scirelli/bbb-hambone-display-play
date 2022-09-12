from typing import Tuple

try:
    from Adafruit_BBIO import GPIO  # pylint: disable=no-name-in-module
except ModuleNotFoundError:
    from .Adafruit_BBIO import GPIO


__all__: Tuple[str, ...] = ("GPIO",)
