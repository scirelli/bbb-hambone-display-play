# pylint: disable=wrong-import-position unused-import wrong-import-order
# flake8: noqa E402
import sys
from os.path import abspath, dirname, join, realpath

from .environment import ENV
from .logger.logger import create_logger

if ENV == "prod":
    raise ImportError("Unable to import mock GPIO library in production")

sys.path.append(abspath(join(dirname(realpath(__file__)), "../", "../", "tests")))
from unit.fixtures.Adafruit_BBIO import GPIO  # isort:skip # noqa

logger = create_logger("AdaFruit_BBIO_MOCK")
logger.warning(
    "\n\n************************************************\n**** IMPORTING MOCKED ADAFRUIT_GPIO LIBRARY ****\n************************************************\n\n"
)
