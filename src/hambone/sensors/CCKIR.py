from __future__ import annotations

from enum import Enum, unique
from logging import Logger
from typing import Dict

import adafruit_ads1x15.ads1015 as ADS
import board
import busio
from adafruit_ads1x15.analog_in import AnalogIn
from typing_extensions import TypedDict

from ..logger.logger import create_logger

DEFAULT_I2C_ADDR = 0x48  # For the ADS11x5
A0_L_ADDR = DEFAULT_I2C_ADDR
A0_H_ADDR = DEFAULT_I2C_ADDR + 0x01

BOARD_1_ADDR = A0_L_ADDR
BOARD_2_ADDR = A0_H_ADDR
MAX_CHANNELS = 8  # Two boards 4 channels each
USEABLE_CHANNELS = MAX_CHANNELS - 2  # We only have six sensors

DEFAULT_LOGGER = create_logger("CCKIR")


class CCKIR:
    @unique
    class Sensor(Enum):
        LEFT_FRONT = 0
        LEFT_MIDDLE = 1
        LEFT_REAR = 2

        RIGHT_FRONT = 3
        RIGHT_MIDDLE = 4
        RIGHT_REAR = 5

    SensorPair = Dict[Sensor, int]

    class Config(TypedDict, total=False):
        logger: Logger

    def __init__(self, config: CCKIR.Config):
        self._logger: Logger = config.get("logger", DEFAULT_LOGGER)
        self._sensors: list[AnalogIn] = []

        self._setup()

    def _setup(self) -> None:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads1 = ADS.ADS1015(i2c, address=BOARD_1_ADDR)
        ads2 = ADS.ADS1015(i2c, address=BOARD_2_ADDR)
        self._sensors = [
            # left side
            # front_left
            AnalogIn(ads1, ADS.P0),
            # middle_left
            AnalogIn(ads1, ADS.P1),
            # rear_left
            AnalogIn(ads1, ADS.P2),
            # right side
            # front_right
            AnalogIn(ads2, ADS.P0),
            # middle_right
            AnalogIn(ads2, ADS.P1),
            # rear_right
            AnalogIn(ads2, ADS.P2),
        ]

    def get_sensors(self) -> list[AnalogIn]:
        return self._sensors

    def get_sensor(self, index: CCKIR.Sensor) -> AnalogIn:
        return self._sensors[index.value]

    def read_sensor(self, index: CCKIR.Sensor) -> int:
        return self._sensors[index.value].value

    def read_front(self) -> CCKIR.SensorPair:
        return {
            CCKIR.Sensor.LEFT_FRONT: self._sensors[CCKIR.Sensor.LEFT_FRONT.value].value,
            CCKIR.Sensor.RIGHT_FRONT: self._sensors[
                CCKIR.Sensor.RIGHT_FRONT.value
            ].value,
        }

    def read_middle(self) -> CCKIR.SensorPair:
        return {
            CCKIR.Sensor.LEFT_MIDDLE: self._sensors[
                CCKIR.Sensor.LEFT_MIDDLE.value
            ].value,
            CCKIR.Sensor.RIGHT_MIDDLE: self._sensors[
                CCKIR.Sensor.RIGHT_MIDDLE.value
            ].value,
        }

    def read_rear(self) -> CCKIR.SensorPair:
        return {
            CCKIR.Sensor.LEFT_REAR: self._sensors[CCKIR.Sensor.LEFT_REAR.value].value,
            CCKIR.Sensor.RIGHT_REAR: self._sensors[CCKIR.Sensor.RIGHT_REAR.value].value,
        }
