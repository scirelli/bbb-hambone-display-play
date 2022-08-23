from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import Logger
from threading import Lock, Thread
from time import sleep
from typing import Any, Optional, Tuple, cast

from adafruit_ads1x15.analog_in import AnalogIn

from ..logger.logger import create_logger

DEFAULT_MAX_THREAD_RUNTIME_S = 2 * 60
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
    _data_lock: Lock = Lock()

    @dataclass
    class ChannelReading:  # type: ignore
        pin: AnalogIn  # type: ignore
        min_value: Optional[int] = None
        max_value: Optional[int] = None

    @staticmethod
    def _default_thread(name: str) -> None:
        raise IRNoThreadExcption()

    def __init__(self, config: dict[str, Any]):
        self._logger: Logger = config.get("logger", DEFAULT_LOGGER)
        self._max_thread_runtime_sec: int = config.get(
            "maxThreadRuntimeSeconds", DEFAULT_MAX_THREAD_RUNTIME_S
        )

        self._calibrating: bool = False
        self._calibrationthread: Thread = Thread(target=MinMax._default_thread)
        self._channels: list[MinMax.ChannelReading] = [
            MinMax.ChannelReading(s) for s in config.get("sensors", [])
        ]

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
            self._logger.info("Calibrating...")
            with MinMax._data_lock:
                for channel in self._channels:
                    v = channel.pin.value
                    self._logger.debug(f"value = {v}")
                    if channel.min_value is None or v < channel.min_value:
                        channel.min_value = v
                    if channel.max_value is None or v > channel.max_value:
                        channel.max_value = v
            sleep(0.1)
        self._logger.info("Calibration Finished - we have min and max")
        self._logger.debug(f"Results: {self._channels}")
