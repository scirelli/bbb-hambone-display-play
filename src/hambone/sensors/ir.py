"""
ADS11x5 Pins
ADDR - I2C address selection pin
   Default address is 0x48
   The ADS11x5 chips have a base 7-bit I2C address of 0x48 (1001000) and a addressing scheme that allows different addresses using just one address pin (ADDR).
   ┏━━━━━┯━━━━━┓
   ┃ I2C │ADDR ┃
   ┃ ADDR│Pin  ┃
   ┠─────┼─────┨
   ┃0x48 │GND  ┃
   ┠─────┼─────┨
   ┃0x49 │VIN  ┃
   ┠─────┼─────┨
   ┃0x4A │SDA  ┃
   ┠─────┼─────┨
   ┃0x4B │SCL  ┃
   ┗━━━━━┷━━━━━┛

ALRT           - Digital comparator output or conversion ready, can be set up and used for interrupt / asynchronous read.
A+ and A-      - ADC power supply (VIN through a ferrite) and ADC ground (digital GND through a ferrite) these are OUTPUTs not inputs!
A0, A1, A2, A3 - ADC input pins for each channel.

Single Ended vs. Differential Inputs:
The ADS1x15 breakouts support up to 4 Single Ended or 2 Differential inputs.
Single Ended inputs measure the voltage between the analog input channel (A0-A3) and analog ground (GND).
Differential inputs measure the voltage between two analog input channels.  (A0&A1 or A2&A3).
Probe the I2C busses for connected devices:
$ i2cdetect -y -r 0
$ i2cdetect -y -r 1

https://www.ti.com/lit/ds/symlink/ads1015.pdf?ts=1661338223297
Input signal vs idea output code
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━┓
┃ INPUT SINGAL               │ IDEAL OUTPUT CODE  ┃
┃ Vin = (Vanip - Vainn)      │                    ┃
┠────────────────────────────┼────────────────────┨
┃ >= +FS (2^11 - 1)/2^11     │ 0x7FF0             ┃
┠────────────────────────────┼────────────────────┨
┃ +FS/2^11                   │ 0x0010             ┃
┠────────────────────────────┼────────────────────┨
┃ 0                          │ 0x0000             ┃
┠────────────────────────────┼────────────────────┨
┃ -FS/2^11                   │ 0xFFF0             ┃
┠────────────────────────────┼────────────────────┨
┃ <= -FS                     │ 0x8000             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━┛
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import Logger
from threading import Lock, Thread
from time import sleep
from typing import Optional, Sequence, Tuple, TypedDict, cast

from adafruit_ads1x15.analog_in import AnalogIn

from ..logger.logger import create_logger
from ..stats.stats import AsTableStr

DEFAULT_LOGGER = create_logger("IR")


class IRExceptoin(Exception):
    pass


class CalibrationInProgress(IRExceptoin):
    pass


class IRNoThreadExcption(IRExceptoin):
    pass


class Sensor(AnalogIn):  # type: ignore
    pass


class Calibrator(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> Tuple[Tuple[int, int], ...]:
        return ()


class MinMax(Calibrator):
    DEFAULT_MAX_THREAD_RUNTIME_S: float = 2 * 60
    DEFAULT_READ_DELAY_S: float = 0.1
    _data_lock: Lock = Lock()

    class Config(TypedDict, total=False):
        maxThreadRuntimeSeconds: float
        readDelaySeconds: float
        logger: Logger
        sensors: list[AnalogIn]

    @dataclass
    class _ChannelReading:  # type: ignore
        pin: AnalogIn  # type: ignore
        min_value: Optional[int] = None
        max_value: Optional[int] = None

    class _Stats(AsTableStr):
        def __init__(self) -> None:
            self._readings: int = 0

        def get_headers(self) -> Sequence[str]:
            return ["Readings"]

        def get_row(self) -> Sequence[str]:
            return [str(self._readings)]

        def inc_readings(self) -> MinMax._Stats:
            self._readings += 1
            return self

        def reset(self) -> MinMax._Stats:
            self._readings = 0
            return self

    @staticmethod
    def _default_thread(name: str) -> None:
        raise IRNoThreadExcption()

    def __init__(self, config: MinMax.Config):
        self._logger: Logger = config.get("logger", DEFAULT_LOGGER)
        self._max_thread_runtime_sec: float = config.get(
            "maxThreadRuntimeSeconds", MinMax.DEFAULT_MAX_THREAD_RUNTIME_S
        )
        self._read_delay_sec: float = config.get(
            "readDelaySeconds", MinMax.DEFAULT_READ_DELAY_S
        )

        self._calibrating: bool = False
        self._calibrationthread: Thread = Thread(target=MinMax._default_thread)
        self._channels: list[MinMax._ChannelReading] = [
            MinMax._ChannelReading(s) for s in config.get("sensors", [])
        ]
        self._stats = MinMax._Stats()

    def add(self, sensor: AnalogIn) -> MinMax:  # type: ignore
        if self._calibrating:
            raise CalibrationInProgress()

        self._channels.append(sensor)
        return self

    def start(self) -> None:
        if self._calibrating:
            raise CalibrationInProgress()

        self._calibrating = True
        self._calibrationthread = Thread(target=self._thread_function)
        self._calibrationthread.start()

    def stop(self) -> Tuple[Tuple[int, int], ...]:
        self._calibrating = False
        self._calibrationthread.join()
        self._calibrationthread = Thread(target=MinMax._default_thread)
        return tuple(
            (cast(int, c.min_value), cast(int, c.max_value)) for c in self._channels
        )

    def _thread_function(self) -> None:
        self._logger.info("Calibrating Started")

        while self._calibrating:
            with MinMax._data_lock:
                for channel in self._channels:
                    v = channel.pin.value
                    self._logger.debug(f"read: {v}")
                    if channel.min_value is None or v < channel.min_value:
                        channel.min_value = v
                    if channel.max_value is None or v > channel.max_value:
                        channel.max_value = v
            self._stats.inc_readings()
            sleep(self._read_delay_sec)

        self._logger.info("Calibration Finished - we have min and max")
