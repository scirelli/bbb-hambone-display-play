from enum import Enum, unique


@unique
class PinState(Enum):
    LOW: int = 0
    HIGH: int = 1


class Pin:
    _state: int

    def __init__(self, state: int):
        self._state = state

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, value: int) -> None:
        self._state = value
