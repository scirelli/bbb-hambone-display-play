import pytest
from unit.fixtures.Adafruit_BBIO.GPIO import create_GPIO

from hambone import gpio


@pytest.fixture(autouse=True)
def mock_gpio_module(monkeypatch):
    monkeypatch.setattr(gpio, "GPIO", create_GPIO("test_driver"))
