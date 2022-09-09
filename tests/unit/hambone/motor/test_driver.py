# pylint: disable=redefined-outer-name, protected-access
from unittest.mock import MagicMock, call

import pytest
from unit.fixtures.Adafruit_BBIO.GPIO import create_GPIO

from hambone.motor import driver
from hambone.motor.driver import MotorDriver


@pytest.fixture(autouse=True)
def mock_gpio(monkeypatch):
    monkeypatch.setattr(driver, "GPIO", create_GPIO("test_driver"))
    return driver.GPIO


# ---------------- MotorDriver -----------------------


@pytest.fixture(scope="function")
def motor_driver_mock(monkeypatch, request):
    for method in request.param:
        monkeypatch.setattr(MotorDriver, method, MagicMock(name=method))


@pytest.fixture(scope="function")
def motor_driver_instance(request):
    return MotorDriver(request.param)


@pytest.mark.parametrize(
    (
        "motor_driver_mock",
        "motor_driver_instance",
    ),
    (
        (
            ["stop"],
            {"motorIN1Pin": "P8_1", "motorIN2Pin": "P8_2"},
        ),
    ),
    indirect=["motor_driver_mock", "motor_driver_instance"],
    ids=("",),
)
@pytest.mark.usefixtures("motor_driver_mock")
def test_gpio_setup_sets_motor_pins_to_a_default_state(
    mock_gpio, motor_driver_instance
) -> None:
    assert mock_gpio.setup.call_count == 2
    mock_gpio.setup.assert_has_calls(
        (
            call("P8_1", mock_gpio.OUT, pull_up_down=mock_gpio.PUD_DOWN),
            call("P8_2", mock_gpio.OUT, pull_up_down=mock_gpio.PUD_DOWN),
        )
    )
    motor_driver_instance.stop.assert_called_once()
