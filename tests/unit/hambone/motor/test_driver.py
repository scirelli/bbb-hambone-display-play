# pylint: disable=redefined-outer-name, protected-access
import logging
from unittest.mock import MagicMock, call, create_autospec

import pytest
from unit.fixtures.Adafruit_BBIO.GPIO import create_GPIO

from hambone.motor import driver
from hambone.motor.driver import MotorDriver, MotorLimits


@pytest.fixture(autouse=True)
def mock_gpio(monkeypatch):
    monkeypatch.setattr(driver, "GPIO", create_GPIO("test_driver"))
    return driver.GPIO


@pytest.fixture(autouse=True)
def mock_logger():
    return create_autospec(logging, spec_set=True)


# ---------------- MotorDriver -----------------------


@pytest.fixture(scope="function")
def motor_driver_mock(monkeypatch, request):
    for method in request.param:
        monkeypatch.setattr(MotorDriver, method, MagicMock(name=method))


@pytest.fixture(scope="function")
def motor_driver_instance(request):
    return MotorDriver(request.param)


# ---------------- MotorDriver._gpio_setup -----------------------
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
def test__gpio_setup_puts_the_motor_into_a_default_state(
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


# ---------------- MotorDriver.forward -----------------------
@pytest.mark.parametrize(
    (
        "motor_driver_mock",
        "motor_driver_instance",
    ),
    (
        (
            ["_gpio_setup", "set_state"],
            {"motorIN1Pin": "P8_1", "motorIN2Pin": "P8_2"},
        ),
    ),
    indirect=["motor_driver_mock", "motor_driver_instance"],
    ids=("",),
)
@pytest.mark.usefixtures("motor_driver_mock")
def test_forward_sets_puts_the_motor_into_a_forward_configuration(
    motor_driver_instance,
) -> None:
    motor_driver_instance.forward()
    motor_driver_instance.set_state.assert_called_with(MotorDriver.State.FORWARD)


# ---------------- MotorDriver.backward -----------------------
@pytest.mark.parametrize(
    (
        "motor_driver_mock",
        "motor_driver_instance",
    ),
    (
        (
            ["_gpio_setup", "set_state"],
            {"motorIN1Pin": "P8_1", "motorIN2Pin": "P8_2"},
        ),
    ),
    indirect=["motor_driver_mock", "motor_driver_instance"],
    ids=("",),
)
@pytest.mark.usefixtures("motor_driver_mock")
def test_backward_sets_puts_the_motor_into_a_backward_configuration(
    motor_driver_instance,
) -> None:
    motor_driver_instance.backward()
    motor_driver_instance.set_state.assert_called_with(MotorDriver.State.BACKWARD)


# ---------------- MotorDriver.stop -----------------------
@pytest.mark.parametrize(
    (
        "motor_driver_mock",
        "motor_driver_instance",
    ),
    (
        (
            ["_gpio_setup", "set_state"],
            {"motorIN1Pin": "P8_1", "motorIN2Pin": "P8_2"},
        ),
    ),
    indirect=["motor_driver_mock", "motor_driver_instance"],
    ids=("",),
)
@pytest.mark.usefixtures("motor_driver_mock")
def test_stop_sets_puts_the_motor_into_a_stop_configuration(
    motor_driver_instance,
) -> None:
    motor_driver_instance.stop()
    motor_driver_instance.set_state.assert_called_with(MotorDriver.State.STOP)


# ---------------- MotorDriver.get_state -----------------------
@pytest.mark.parametrize(
    ("motor_driver_mock", "motor_driver_instance", "expected_state"),
    (
        (
            ["_gpio_setup"],
            {"motorIN1Pin": "P8_1", "motorIN2Pin": "P8_2"},
            MotorDriver.State.STOP,
        ),
    ),
    indirect=["motor_driver_mock", "motor_driver_instance"],
    ids=("",),
)
@pytest.mark.usefixtures("motor_driver_mock")
def test_get_state_puts_the_motor_into_a_given_configuration(
    motor_driver_instance, expected_state
) -> None:
    assert motor_driver_instance.get_state() == expected_state


# ---------------- MotorDriver.set_state -----------------------
@pytest.mark.parametrize(
    (
        "motor_driver_instance",
        "given",
        "expected",
    ),
    (
        (
            {"motorIN1Pin": "P8_1", "motorIN2Pin": "P8_2"},
            MotorDriver.State.FORWARD,
            (call("P8_1", driver.GPIO.LOW), call("P8_2", driver.GPIO.HIGH)),
        ),
        (
            {"motorIN1Pin": "P8_1", "motorIN2Pin": "P8_2"},
            MotorDriver.State.BACKWARD,
            (call("P8_2", driver.GPIO.LOW), call("P8_1", driver.GPIO.HIGH)),
        ),
        (
            {"motorIN1Pin": "P8_1", "motorIN2Pin": "P8_2"},
            MotorDriver.State.STOP,
            (call("P8_2", driver.GPIO.LOW), call("P8_1", driver.GPIO.LOW)),
        ),
        (
            {"motorIN1Pin": "P8_1", "motorIN2Pin": "P8_2"},
            MotorDriver.State.BREAK,
            (call("P8_2", driver.GPIO.HIGH), call("P8_1", driver.GPIO.HIGH)),
        ),
    ),
    indirect=["motor_driver_instance"],
    ids=("forward", "backward", "stop", "break"),
)
def test_set_state_puts_the_motor_into_the_requested_state(
    mock_gpio, motor_driver_instance, given, expected
) -> None:
    motor_driver_instance.set_state(given)
    assert mock_gpio.output.call_count == 2
    mock_gpio.output.assert_has_calls(expected)
    assert motor_driver_instance._state == given


# ---------------- MotorLimits -----------------------
@pytest.fixture(scope="function")
def motorlimits_instance(request, mock_logger):
    return MotorLimits({**request.param, "logger": mock_logger})


# ---------------- MotorLimits._gpio_setup -----------------------
@pytest.mark.parametrize(
    ("motorlimits_instance",),
    (({"frontLimitSwitchPin": "P8_1", "rearLimitSwitchPin": "P8_2"},),),
    indirect=["motorlimits_instance"],
    ids=("",),
)
@pytest.mark.usefixtures("motorlimits_instance")
def test__gpio_setup_puts_the_limit_switches_into_a_default_state(mock_gpio) -> None:
    assert mock_gpio.setup.call_count == 2
    mock_gpio.setup.assert_has_calls(
        (
            call("P8_1", mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP),
            call("P8_2", mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP),
        )
    )


# ---------------- MotorLimits.is_front_limit_pressed -----------------------
@pytest.mark.parametrize(
    ("motorlimits_instance",),
    (({"frontLimitSwitchPin": "P8_1", "rearLimitSwitchPin": "P8_2"},),),
    indirect=["motorlimits_instance"],
    ids=("",),
)
def test_is_front_limit_pressed_should_return_the_state_of_the_limit_switch(
    mock_gpio, motorlimits_instance
) -> None:
    mock_gpio.input.side_effect = lambda *_: False
    assert motorlimits_instance.is_front_limit_pressed() is True, "limit switch pressed"
    mock_gpio.input.side_effect = lambda *_: True
    assert (
        motorlimits_instance.is_front_limit_pressed() is False
    ), "limit switch not pressed"


# ---------------- MotorLimits.is_front_limit_pressed -----------------------
@pytest.mark.parametrize(
    ("motorlimits_instance",),
    (({"frontLimitSwitchPin": "P8_1", "rearLimitSwitchPin": "P8_2"},),),
    indirect=["motorlimits_instance"],
    ids=("",),
)
def test_is_rear_limit_pressed_should_return_the_state_of_the_limit_switch(
    mock_gpio, motorlimits_instance
) -> None:
    mock_gpio.input.side_effect = lambda *_: False
    assert motorlimits_instance.is_rear_limit_pressed() is True, "limit switch pressed"
    mock_gpio.input.side_effect = lambda *_: True
    assert (
        motorlimits_instance.is_rear_limit_pressed() is False
    ), "limit switch not pressed"
