from enum import Enum, unique


@unique
class PinState(Enum):
    LOW: int = 0
    HIGH: int = 1


# Make these more realistic with physical pins and headers
class BBB:
    pins: dict[str, PinState] = {
        "P8_7": PinState.LOW,
        "P8_8": PinState.LOW,
        "P8_9": PinState.LOW,
        "P8_10": PinState.HIGH,
        "P8_12": PinState.HIGH,
    }
