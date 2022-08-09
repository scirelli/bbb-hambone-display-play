from __future__ import annotations

from logging import Logger
from typing import Any

from ..logger.logger import create_logger
from .Color import HSVtoRGB
from .NeoPixelPRU import NeoPixelPRU

DEFAULT_LOGGER = create_logger("CCKDisplay")


class CCKDisplay:
    display_segment_index = NeoPixelPRU.SEGMENT_ONE
    scanner_segment_index = NeoPixelPRU.SEGMENT_TWO
    presenter_segment_index = NeoPixelPRU.SEGMENT_THREE

    FLASH_RATE_MS = 1000  # On for FLASH_RATE_MS off for FLASH_RATE_MS
    COLORS: dict[str, list[float]] = {
        "BLACK": [0, 0, 0],
        "OFF": [0, 0, 0],
        "RED": [255, 0, 0],
        "GREEN": [0, 255, 0],
    }

    def __init__(self, config: dict[str, Any]):
        self._log: Logger = config.get("logger", DEFAULT_LOGGER)
        self._neopixel_controller: NeoPixelPRU = NeoPixelPRU(
            config.get("neoPixelConfig", {})
        )

    def set_display_color(self, r: float, g: float, b: float) -> CCKDisplay:
        return self.set_segment(CCKDisplay.display_segment_index, r, g, b)

    def display_off(self) -> CCKDisplay:
        return self.set_segment(
            CCKDisplay.display_segment_index, *CCKDisplay.COLORS["OFF"]
        )

    def set_scanner_color(self, r: float, g: float, b: float) -> CCKDisplay:
        return self.set_segment(CCKDisplay.scanner_segment_index, r, g, b)

    def scanner_off(self) -> CCKDisplay:
        return self.set_segment(
            CCKDisplay.scanner_segment_index, *CCKDisplay.COLORS["OFF"]
        )

    def set_presenter_color(self, r: float, g: float, b: float) -> CCKDisplay:
        return self.set_segment(CCKDisplay.presenter_segment_index, r, g, b)

    def presenter_off(self) -> CCKDisplay:
        return self.set_segment(
            CCKDisplay.presenter_segment_index, *CCKDisplay.COLORS["OFF"]
        )

    def set_all_segments_color(self, r: float, g: float, b: float) -> CCKDisplay:
        self.set_display_color(r, g, b)
        self.set_scanner_color(r, g, b)
        self.set_presenter_color(r, g, b)
        return self

    def all_segments_off(self) -> CCKDisplay:
        self.display_off()
        self.scanner_off()
        self.presenter_off()
        return self

    def presenter_timeout_percentage(self, percent: float) -> CCKDisplay:
        rgb: dict[str, int] = CCKDisplay.fade_green_down_to_red(percent)
        return self.set_presenter_color(rgb["r"], rgb["g"], rgb["b"])

    def set_segment(self, index: int, r: float, g: float, b: float) -> CCKDisplay:
        self._neopixel_controller.set_segment(index, r, g, b)
        return self

    @staticmethod
    def fade_green_down_to_red(percentage: float) -> dict[str, int]:
        return HSVtoRGB(120 * percentage / 360, 1.0, 1.0)
