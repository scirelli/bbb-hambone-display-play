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
        self._x = 0
        self._len = len(display.pixels)
        self._max_animation_time_ns = 10 * NANO_SEC_IN_SEC
        self._total_time_ns = 0
        self._prevTime = perf_counter_ns()

    def animate(self):
        cur_t = perf_counter_ns()
        elapsed_time_ns = cur_t - self._prevTime
        self._prevTime = cur_t
        self._total_time_ns = self._total_time_ns + elapsed_time_ns
        # dt = self._total_time_ns / self._max_animation_time_ns

        for i, p in enumerate(self.display.get_display()):
            r = (self._amp * (math.cos(2 * math.pi * self._f * (i - self._phase - 0 * self._shift) / self._len) + 1)) + 1
            g = (self._amp * (math.cos(2 * math.pi * self._f * (i - self._phase - 1 * self._shift) / self._len) + 1)) + 1
            b = (self._amp * (math.cos(2 * math.pi * self._f * (i - self._phase - 2 * self._shift) / self._len) + 1)) + 1
            p.r = r
            p.g = g
            p.b = b
        self._x = self._x + 1
        self._phase = self._phase + 1
