# pylint: disable=wrong-import-position unused-import wrong-import-order
# flake8: noqa E402
import sys
from os.path import abspath, dirname, join, realpath
from typing import Any, Callable

from ..environment import ENV
from ..logger.logger import create_logger
from .hardware_sim.bbb import BBB
from .hardware_sim.pin import PinState

if ENV == "prod":
    raise ImportError("Unable to import mock GPIO library in production")

sys.path.append(
    abspath(join(dirname(realpath(__file__)), "../", "../", "../", "tests"))
)
from unit.fixtures.Adafruit_BBIO import GPIO  # isort:skip # noqa

logger = create_logger("MOCK:AdaFruit_BBIO")
logger.warning(
    "\n\n************************************************\n**** IMPORTING MOCKED ADAFRUIT_GPIO LIBRARY ****\n************************************************\n\n"
)

# ########### Create a simulation of the Paw hardware #################
bbb: BBB = BBB()
HIGH = 1
LOW = 0
FRONT_LIMIT_SWITCH_PIN = "P8_12"
REAR_LIMIT_SWITCH_PIN = "P8_10"
DOOR_SWITCH_PIN = "P8_8"
MOTOR_IN1_PIN = "P8_7"  # Drive backward (toward BBB)
MOTOR_IN2_PIN = "P8_9"  # Drive forward (away from BBB)


# Set the limit switches LOW so they always read as pressed.
bbb.write_named_pin(FRONT_LIMIT_SWITCH_PIN, PinState.LOW.value)
bbb.write_named_pin(REAR_LIMIT_SWITCH_PIN, PinState.LOW.value)


def _generic_side_effect_factory(name: str) -> Callable[..., None]:
    def f(*args: Any, **kwargs: dict[Any, Any]) -> None:
        logger.info("%s(%s, %s)", name, args, kwargs)

    return f


def _output_side_effect(pin: str, state: int) -> None:
    logger.info("output(%s, %s)", pin, "HIGH" if state else "LOW")
    bbb.write_named_pin(pin, state)


def _input_side_effect(pin: str) -> int:
    logger.info("input(%s) -> %s", pin, bbb.read_named_pin(pin))
    return bbb.read_named_pin(pin)


GPIO.setup.side_effect = _generic_side_effect_factory("setup")
GPIO.cleanup.side_effect = _generic_side_effect_factory("cleanup")
GPIO.input.side_effect = _input_side_effect
GPIO.output.side_effect = _output_side_effect
