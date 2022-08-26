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
    _reference_count: dict[str, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in AdaGPIOSingleton._instances:
            AdaGPIOSingleton._instances[cls] = super().__call__(*args, **kwargs)
            AdaGPIOSingleton._reference_count[cls] = 0
        AdaGPIOSingleton._reference_count[cls] += 1
        DEFAULT_LOGGER.debug(AdaGPIOSingleton._reference_count[cls])
        return AdaGPIOSingleton._instances[cls]

    def __del__(cls):
        DEFAULT_LOGGER.debug(AdaGPIOSingleton._instances)
        DEFAULT_LOGGER.debug(cls._instances)
        DEFAULT_LOGGER.debug(AdaGPIOSingleton._reference_count[cls])
        AdaGPIOSingleton._reference_count[cls] -= 1
        if AdaGPIOSingleton._reference_count[cls] <= 0:
            AdaGPIOSingleton._reference_count[cls] = 0
            del AdaGPIOSingleton._instances[cls]
            DEFAULT_LOGGER.debug("GPIO.cleanup is being called")
            # This is recommended to be called in the docs https://github.com/adafruit/adafruit-beaglebone-io-python/blob/master/docs/GPIO.rst
            GPIO.cleanup()
