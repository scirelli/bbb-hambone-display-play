from __future__ import annotations

from logging import Logger
from math import floor
from typing import Any

from neopixel.writer.STDOutWriter import STDOutWriter
from neopixel.writer.Writer import Writer

from .logger import create_logger

DEFAULT_LOGGER = create_logger("NEOPIXEL")
DEFAULT_WRITER = STDOutWriter()
DEFAULT_LED_COUNT = (
    42  # Defined in PRU. This is the max number of LEDs unless changed in PRU firmware.
)
SEGMENT_COUNT = 4  # Defined in PRU
SEGMENT_ALL = 0  # Defined in PRU
SEGMENT_ONE = 1  # Defined in PRU
SEGMENT_TWO = 2  # Defined in PRU
SEGMENT_THREE = 3  # Defined in PRU


class NeoPixelPRU:
    SEGMENT_COUNT = SEGMENT_COUNT
    SEGMENT_ALL = SEGMENT_ALL
    SEGMENT_ONE = SEGMENT_ONE
    SEGMENT_TWO = SEGMENT_TWO
    SEGMENT_THREE = SEGMENT_THREE

    def __init__(self, config: dict[str, Any]):
        self._log: Logger = config.get("logger", DEFAULT_LOGGER)
        self._writer: Writer = config.get("writer", DEFAULT_WRITER)
        self._led_count: int = int(config.get("ledCount", DEFAULT_LED_COUNT))

        self._color_destination_buffer_index: int = self._led_count
        self._segment_start_index: int = self._led_count + self._led_count
        self._segment_one_index: int = self._segment_start_index

    def set_logger(self, logger: Logger) -> NeoPixelPRU:
        self._log = logger
        return self

    def set_color_buffer(self, index: int, r: float, g: float, b: float) -> NeoPixelPRU:
        if not self.is_valid_display_index(index):
            self._log.warn("Index out of range.")
            return self

        self._write(f"{index} {float(r)} {float(g)} {float(b)}")
        return self

    def set_color(self, index: int, r: float, g: float, b: float) -> NeoPixelPRU:
        self.set_color_buffer(index, r, g, b)
        self.draw()
        return self

    def set_destination_color_buffer(
        self, index: int, r: float, g: float, b: float
    ) -> NeoPixelPRU:
        if not self.is_valid_display_index(index):
            self._log.warn("Index out of range.")
            return self

        self._write(
            f"{self._color_destination_buffer_index + index} {floor(r)} {floor(g)} {floor(b)}"
        )
        return self

    def set_destination_color(
        self, index: int, r: float, g: float, b: float
    ) -> NeoPixelPRU:
        self.set_destination_color_buffer(index, r, g, b)
        self.draw()
        return self

    def set_segment_buffer(
        self, index: int, r: float, g: float, b: float
    ) -> NeoPixelPRU:
        if not self.is_valid_segment_index(index):
            self._log.warn("Invalid segment index")
            return self

        self._write(
            f"{index + self._segment_start_index} {floor(r)} {floor(g)} {floor(b)}"
        )
        return self

    def set_segment(self, index: int, r: float, g: float, b: float) -> NeoPixelPRU:
        self.set_segment_buffer(index, r, g, b)
        self.draw()
        return self

    def is_valid_display_index(self, index: int) -> bool:
        return 0 <= index < self._led_count

    def is_valid_segment_index(self, index: int) -> bool:
        return 0 <= index < SEGMENT_COUNT

    def clear(self) -> NeoPixelPRU:
        self._write("-2 0 0 0")
        return self

    def draw(self) -> NeoPixelPRU:
        self._write("-1 0 0 0")
        return self

    def _write(self, s: str) -> NeoPixelPRU:
        self._writer.write(bytearray(s + "\n", "ascii"))
        return self
