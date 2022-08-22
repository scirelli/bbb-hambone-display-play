#!/usr/bin/env python
# pylint: disable=wrong-import-position unused-import wrong-import-order global-statement
# flake8: noqa E402
import logging
import threading
import time
from typing import Any

import adafruit_ads1x15.ads1015 as ADS
import board
import busio
from adafruit_ads1x15.analog_in import AnalogIn

DEFAULT_I2C_ADDR = 0x48  # For the ADS11x5
A0_L_ADDR = DEFAULT_I2C_ADDR
A0_H_ADDR = DEFAULT_I2C_ADDR + 0x01

BOARD_1_ADDR = A0_L_ADDR
BOARD_2_ADDR = A0_H_ADDR
MAX_VALUE = 0b111111111111


calibrating = False
readings = [0, 0, 0, 0, 0, 0]
calibrationthread = None

i2c = busio.I2C(board.SCL, board.SDA)
ads1 = ADS.ADS1015(i2c, address=BOARD_1_ADDR)
ads2 = ADS.ADS1015(i2c, address=BOARD_2_ADDR)
channels = [
    # left side
    # front_left
    AnalogIn(ads1, ADS.P0),
    # middle_left
    AnalogIn(ads1, ADS.P1),
    # back_left
    AnalogIn(ads1, ADS.P2),
    # right side
    # front_right
    AnalogIn(ads2, ADS.P0),
    # middle_right
    AnalogIn(ads2, ADS.P1),
    # back_right
    AnalogIn(ads2, ADS.P2),
]


def read_sensors() -> None:
    for i, pin in enumerate(channels):
        readings[i] = pin.value


def thread_function(name):
    _min = [None] * 5
    _max = [None] * 5
    logging.info("Calibrating Started(%s)", name)
    while calibrating:
        read_sensors()
        for i in range(0, 5):
            if _min[i] is None or readings[i] < _min[i]:
                _min[i] = readings[i]
            if _max[i] is None or readings[i] > _max[i]:
                _max[i] = readings[i]
        logging.info("Calibrating")
        time.sleep(0.1)
    logging.info("Calibration Finished - we have min and max")
    logging.info("min %s", _min)
    logging.info("max %s", _max)


def start_calibrate():
    global calibrationthread
    global calibrating
    calibrating = True
    calibrationthread = threading.Thread(target=thread_function, args=(1,))
    calibrationthread.start()


def finish_calibrate():
    global calibrationthread
    global calibrating
    calibrating = False
    calibrationthread.join()
    calibrationthread = None


if __name__ == "__main__":
    _format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=_format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info("Before Calibration")
    start_calibrate()
    time.sleep(2)
    finish_calibrate()
    logging.info("All Done!")
