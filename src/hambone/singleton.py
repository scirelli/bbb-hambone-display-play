# type: ignore
from typing import Any

from hambone.gpio import GPIO

from .logger.logger import create_logger

DEFAULT_LOGGER = create_logger("Singleton")


class Singleton(type):
    _instances: dict[str, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AdaGPIOSingleton(type):
    """
    This metaclass was created in an attempt to remove the need for the end user to have to remember/know to call GPIO.cleanup()
    These classes should not have more than one instance attempting to control HAMBone hardware components.
    Will need to implement thread safety if threads are going to be used.
    """

    _instances: dict[str, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def __del__(cls):
        del AdaGPIOSingleton._instances[cls]
        if len(AdaGPIOSingleton._instances) == 0:
            DEFAULT_LOGGER.debug("GPIO.cleanup is being called")
            GPIO.cleanup()
