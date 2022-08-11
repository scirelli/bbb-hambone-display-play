#!/usr/bin/env python3
from json import dump
from sys import stderr, stdout
from time import perf_counter_ns

from Adafruit_BBIO import GPIO  # pylint: disable=no-name-in-module

FRONT_LIMIT_SWITCH_PIN = "P8_12"
REAR_LIMIT_SWITCH_PIN = "P8_10"
DOOR_SWITCH_PIN = "P8_8"
MOTOR_IN1_PIN = "P8_7"  # Drive backward (toward BBB)
MOTOR_IN2_PIN = "P8_9"  # Drive forward (away from BBB)

GPIO.setup(FRONT_LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(REAR_LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(MOTOR_IN1_PIN, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(MOTOR_IN2_PIN, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)


def eprint(*args, **kwargs) -> None:  # type: ignore
    print(*args, file=stderr, **kwargs)


def main(times: list[int]) -> None:  # pylint: disable=redefined-outer-name
    motorStop()
    motorForward()

    startTime: int = perf_counter_ns()
    totalTime: int = 60 * 1000000000
    f_pressed: bool = False
    r_pressed: bool = False

    while True:
        if (perf_counter_ns() - startTime) >= totalTime:
            break

        if GPIO.input(FRONT_LIMIT_SWITCH_PIN):
            if f_pressed:
                eprint("Front limit switch released")
                f_pressed = False
        else:
            motorBackward()
            if not f_pressed:
                eprint("Front limit switch pressed")
                times.append(perf_counter_ns())
                f_pressed = True

        if GPIO.input(REAR_LIMIT_SWITCH_PIN):
            if r_pressed:
                eprint("Rear limit switch released")
                r_pressed = False
        else:
            motorForward()
            if not r_pressed:
                eprint("Rear limit switch pressed")
                times.append(perf_counter_ns())
                r_pressed = True

        # if GPIO.input(DOOR_SWITCH_PIN):
        #     eprint("Door switch pressed")
        # else:
        #     eprint("Door switch released")


def motorForward() -> None:
    GPIO.output(MOTOR_IN1_PIN, GPIO.LOW)
    GPIO.output(MOTOR_IN2_PIN, GPIO.HIGH)


def motorBackward() -> None:
    GPIO.output(MOTOR_IN2_PIN, GPIO.LOW)
    GPIO.output(MOTOR_IN1_PIN, GPIO.HIGH)


def motorStop() -> None:
    GPIO.output(MOTOR_IN2_PIN, GPIO.LOW)
    GPIO.output(MOTOR_IN1_PIN, GPIO.LOW)


if __name__ == "__main__":
    times: list[int] = []
    try:
        main(times)
    except BaseException:
        eprint("Handing kb interrupt")
        raise
    finally:
        motorStop()
        GPIO.cleanup()
        dump(times, stdout, indent="\t")
