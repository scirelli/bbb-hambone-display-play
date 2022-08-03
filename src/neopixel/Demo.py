from __future__ import annotations

from time import perf_counter_ns, sleep

from neopixel.CCKDisplay import CCKDisplay

MILLI_SECOND_IN_NANO_SECOND = 1000000


class Demo:
    FLASH_RATE_MS = 1000  # On for FLASH_RATE_MS off for FLASH_RATE_MS

    COLORS: dict[str, list[float]] = {
        "BLACK": [0, 0, 0],
        "OFF": [0, 0, 0],
        "RED": [255, 0, 0],
        "GREEN": [0, 255, 0],
    }

    def __init__(self, cckDisplay: CCKDisplay):
        self._cck: CCKDisplay = cckDisplay

    def all_Error_Flashing(self, timeMs: float) -> None:
        on: bool = False
        timeNS = timeMs * MILLI_SECOND_IN_NANO_SECOND
        startTimeNS = perf_counter_ns()
        while True:
            dt = perf_counter_ns() - startTimeNS
            on = not on
            if dt >= timeNS:
                self._cck.all_segments_off()
                break

            if on:
                self._cck.set_all_segments_color(*Demo.COLORS["RED"])
            else:
                self._cck.all_segments_off()

            sleep(Demo.FLASH_RATE_MS / 1000)

    def presenter_flashing(self, r: float, g: float, b: float, timeMs: float) -> None:
        self.segment_flashing(CCKDisplay.presenter_segment_index, timeMs, r, g, b)

    def display_flashing(self, r: float, g: float, b: float, timeMs: float) -> None:
        self.segment_flashing(CCKDisplay.display_segment_index, timeMs, r, g, b)

    def scanner_flashing(self, r: float, g: float, b: float, timeMs: float) -> None:
        self.segment_flashing(CCKDisplay.scanner_segment_index, timeMs, r, g, b)

    def check_retract_timer(self, timeMs: float) -> None:
        # Countdown animation
        # Animation goes from all Green to yellow to red. Red represents time out.
        timeNs: float = timeMs * MILLI_SECOND_IN_NANO_SECOND
        startTimeNS = perf_counter_ns()
        while True:
            dt = perf_counter_ns() - startTimeNS
            if dt >= timeNs:
                break
            self._cck.presenter_timeout_percentage(1 - (dt / timeNs))
            sleep(0.001)

    def segment_flashing(  # pylint: disable=too-many-arguments
        self, segment_index: int, timeMs: float, r: float, g: float, b: float
    ) -> None:
        on: bool = False
        timeNs: float = timeMs * MILLI_SECOND_IN_NANO_SECOND

        startTimeNS = perf_counter_ns()
        while True:
            dt = perf_counter_ns() - startTimeNS
            on = not on

            if dt >= timeNs:
                self._cck.set_segment(segment_index, *CCKDisplay.COLORS["OFF"])
                break

            if on:
                self._cck.set_segment(segment_index, r, g, b)
            else:
                self._cck.set_segment(segment_index, *CCKDisplay.COLORS["OFF"])

            sleep(Demo.FLASH_RATE_MS / 1000)
