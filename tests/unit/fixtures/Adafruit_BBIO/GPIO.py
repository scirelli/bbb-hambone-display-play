# type: ignore
from datetime import datetime
from os import path
from tempfile import mkdtemp
from unittest.mock import MagicMock, PropertyMock

from hambone.logger.logger import create_file_logger

tempFilename = path.join(mkdtemp(), f"GPIO_{datetime.now().strftime('%H-%M-%S')}")
logger = create_file_logger("MOCK_GPIO", tempFilename)

GPIO = MagicMock()

type(GPIO).IN = PropertyMock(return_value=1)
type(GPIO).OUT = PropertyMock(return_value=0)
type(GPIO).PUD_DOWN = PropertyMock(return_value=0)
type(GPIO).PUD_UP = PropertyMock(return_value=1)
type(GPIO).LOW = PropertyMock(return_value=0)
type(GPIO).HIGH = PropertyMock(return_value=1)


def _generic_side_effect_factory(name: str):
    def f(*args, **kwargs):
        logger.info("%s(%s, %s)", name, args, kwargs)

    return f


def _output_side_effect(pin: str, direction: int):
    logger.info("output(%s, %s)", pin, "HIGH" if direction else "LOW")


GPIO.setup.side_effect = _generic_side_effect_factory("setup")
GPIO.cleanup.side_effect = _generic_side_effect_factory("cleanup")
GPIO.input.side_effect = _generic_side_effect_factory("input")
GPIO.output.side_effect = _output_side_effect
