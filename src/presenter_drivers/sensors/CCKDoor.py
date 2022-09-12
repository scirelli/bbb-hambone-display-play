from __future__ import annotations

from logging import Logger
from typing import cast

from typing_extensions import TypedDict

from ..gpio import GPIO
from ..logger.logger import create_logger
from ..singleton import AdaGPIOSingleton  # type: ignore

# Default Pins
DOOR_SWITCH_PIN = "P8_8"

DEFAULT_LOGGER = create_logger("DoorDriver")


class AccessDoorSwitch(metaclass=AdaGPIOSingleton):
    class Config(TypedDict, total=False):
        logger: Logger
        doorSwitchPin: str

    def __init__(self, config: AccessDoorSwitch.Config):
        self._logger: Logger = config.get("logger", DEFAULT_LOGGER)
        self._switch_pin: str = config.get("doorSwitchPin", DOOR_SWITCH_PIN)
        self.gpio_setup()

    def gpio_setup(self) -> None:
        GPIO.setup(self._switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_open(self) -> bool:
        return cast(bool, GPIO.input(self._switch_pin))

    def is_closed(self) -> bool:
        return not GPIO.input(self._switch_pin)
