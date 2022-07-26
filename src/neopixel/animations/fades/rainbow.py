#!/usr/bin/env python3
import math
from time import perf_counter_ns

from neopixel.display import Display

from ..Animator import Animator

NANO_SEC_IN_SEC = 1000000000
COLOR_MAX = 255


class Rainbow(Animator):
    def __init__(self, display: Display):
        self.display = display
        self._amp = 12
        self._f = 44
        self._shift = 3
        self._phase = 0
        self._len = len(display.get_display())
        self._max_animation_time_ns = 10 * NANO_SEC_IN_SEC
        self._total_time_ns = 0
        self._prevTime = perf_counter_ns()

    def animate(self) -> None:
        cur_t = perf_counter_ns()
        elapsed_time_ns = cur_t - self._prevTime
        self._prevTime = cur_t
        self._total_time_ns = self._total_time_ns + elapsed_time_ns
        # dt = self._total_time_ns / self._max_animation_time_ns

        for i, p in enumerate(self.display.get_display()):
            r = (
                self._amp
                * (
                    math.cos(
                        2
                        * math.pi
                        * self._f
                        * (i - self._phase - 0 * self._shift)
                        / self._len
                    )
                    + 1
                )
            ) + 1
            g = (
                self._amp
                * (
                    math.cos(
                        2
                        * math.pi
                        * self._f
                        * (i - self._phase - 1 * self._shift)
                        / self._len
                    )
                    + 1
                )
            ) + 1
            b = (
                self._amp
                * (
                    math.cos(
                        2
                        * math.pi
                        * self._f
                        * (i - self._phase - 2 * self._shift)
                        / self._len
                    )
                    + 1
                )
            ) + 1
            p.r = r
            p.g = g
            p.b = b
        self._phase = self._phase + 1


class RainbowB(Animator):
    def __init__(self, display: Display):
        self.display = display
        self._amp = 12
        self._f = 44
        self._shift = 3
        self._phase = 0
        self._its = 0
        self._len = len(display.get_display())
        self._cur_pixel_index = 0
        self._max_animation_time_ns = 10 * NANO_SEC_IN_SEC
        self._total_time_ns = 0
        self._prevTime = perf_counter_ns()

    def animate(self) -> None:
        cur_t = perf_counter_ns()
        elapsed_time_ns = cur_t - self._prevTime
        self._prevTime = cur_t
        self._total_time_ns = self._total_time_ns + elapsed_time_ns
        # dt = self._total_time_ns / self._max_animation_time_ns

        i = self._cur_pixel_index
        p = self.display.get_display()[i]
        r = (
            self._amp
            * (
                math.cos(
                    2
                    * math.pi
                    * self._f
                    * (i - self._phase - 0 * self._shift)
                    / self._len
                )
                + 1
            )
        ) + 1
        g = (
            self._amp
            * (
                math.cos(
                    2
                    * math.pi
                    * self._f
                    * (i - self._phase - 1 * self._shift)
                    / self._len
                )
                + 1
            )
        ) + 1
        b = (
            self._amp
            * (
                math.cos(
                    2
                    * math.pi
                    * self._f
                    * (i - self._phase - 2 * self._shift)
                    / self._len
                )
                + 1
            )
        ) + 1
        p.r = r
        p.g = g
        p.b = b
        self._cur_pixel_index = (i + 1) % self._len
        self._its = self._its + 1
        if self._its % self._len == 0:
            self._phase = self._phase + 1
