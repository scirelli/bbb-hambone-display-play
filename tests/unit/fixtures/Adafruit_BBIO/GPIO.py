# type: ignore
from datetime import datetime
from os import path
from tempfile import mkdtemp
from unittest.mock import MagicMock, PropertyMock

from hambone.logger.logger import create_file_logger

tempFilename = path.join(mkdtemp(), f"GPIO_{datetime.now().strftime('%H-%M-%S')}")
logger = create_file_logger("MOCK_GPIO", tempFilename)


def _generic_side_effect_factory(name: str):
    def f(*args, **kwargs):
        logger.info("%s(%s, %s)", name, args, kwargs)

    return f


def _output_side_effect(pin: str, direction: int):
    logger.info("output(%s, %s)", pin, "HIGH" if direction else "LOW")


def _input_side_effect(pin: str):
    logger.info("input(%s)", pin)
    return GPIO.HIGH


def create_GPIO(name="default_gpio_mock"):
    gpio = MagicMock(name=name)

    type(gpio).IN = PropertyMock(return_value=1)
    type(gpio).OUT = PropertyMock(return_value=0)
    type(gpio).PUD_DOWN = PropertyMock(return_value=0)
    type(gpio).PUD_UP = PropertyMock(return_value=1)
    type(gpio).LOW = PropertyMock(return_value=0)
    type(gpio).HIGH = PropertyMock(return_value=1)

    gpio.setup.side_effect = _generic_side_effect_factory("setup")
    gpio.cleanup.side_effect = _generic_side_effect_factory("cleanup")
    gpio.input.side_effect = _input_side_effect
    gpio.output.side_effect = _output_side_effect

    return gpio


GPIO = create_GPIO()
