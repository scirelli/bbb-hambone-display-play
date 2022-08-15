from typing import Tuple

from .hardwarecontroller import HardwareController
from .pin import Pin, PinState


# Make these more realistic with physical pins and headers
class BBB(HardwareController):
    _NOT_EXIST = 0
    _p8: list[Pin] = [
        Pin(PinState.LOW.value) for _ in range(0, 47)
    ]  # Real pins are 1 to 46. 0 doesn't exist
    _p9: list[Pin] = [Pin(PinState.LOW.value) for _ in range(0, 47)]

    def read_pin(self, pin: int) -> int:
        raise UNKNOWN_PIN

    def write_pin(self, pin: int, state: int) -> None:
        raise UNKNOWN_PIN

    def read_named_pin(self, pin_name: str) -> int:
        header, pin = self._parse_pin_name(pin_name)
        return header[pin].state

    def write_named_pin(self, pin_name: str, state: int) -> None:
        header, pin = self._parse_pin_name(pin_name)
        header[pin].state = PinState(state).value

    def _parse_pin_name(self, pin: str) -> Tuple[list[Pin], int]:
        header, pin = pin.split("_")
        match header.upper():
            case "P8":
                return (self._p8, int(pin))
            case "P9":
                return (self._p9, int(pin))

        raise UNKNOWN_PIN


class HardwareControllerException(Exception):
    pass


class UNKNOWN_PIN(HardwareControllerException):
    pass
