from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter_ns
from typing import Any, Iterable, cast

from neopixel.display import Color, NullDisplay

from ..Animator import Animator

NANO_SEC_IN_SEC = 1000000000
COLOR_MAX = 255


@dataclass
class _Segment:
    start: int = 0
    end: int = 0
    min_color: Color = field(default_factory=Color)
    max_color: Color = field(default_factory=Color)
    cur_color: Color = field(default_factory=Color)

    @staticmethod
    def createSegment(  # pylint: disable=dangerous-default-value
        start: int,
        end: int,
        max_color: dict[str, float],
        min_color: dict[str, float] = {},
        cur_color: dict[str, float] = {},
    ) -> _Segment:
        return _Segment(
            int(start),
            int(end),
            Color(
                float(min_color.get("r", 0)),
                float(min_color.get("g", 0)),
                float(min_color.get("b", 0)),
            ),
            Color(
                float(max_color.get("r", 0)),
                float(max_color.get("g", 0)),
                float(max_color.get("b", 0)),
            ),
            Color(
                float(cur_color.get("r", max_color.get("r", 0))),
                float(cur_color.get("g", max_color.get("g", 0))),
                float(cur_color.get("b", max_color.get("b", 0))),
            ),
        )


class StripFadeTest(Animator):
    """
    config: {
        "display": {},
        "segments": [{
            "start": 0,
            "end": 5,
            "max_color": {
                "r": 0,
                "g": 0,
                "b": 0
            },
            "min_color": {
                "r": 0,
                "g": 0,
                "b": 0
            }
        }],
    }
    """

    def __init__(self, config: dict[str, Any]):
        self._screen: list[Color] = config.get("display", NullDisplay()).get_display()
        self._total_length: int = len(self._screen)
        self._total_time_ns: int = 0
        self._prevTime: int = perf_counter_ns()
        self._iterations: int = 0
        self._segments: list[_Segment] = [
            _Segment.createSegment(**s)
            for s in cast(
                Iterable[dict[str, Any]],
                filter(self._validSegment, config.get("segments", [])),
            )
        ]

    def _validSegment(self, s: dict[str, Any]) -> bool:
        start = int(s.get("start", -1))
        end = int(s.get("end", -1))
        return self._total_length > end >= start >= 0

    def animate(self, dt_ns: int) -> None:
        for s in self._segments:
            r = g = b = 0.0
            if self._iterations & 1:
                r, g, b = s.cur_color.r, s.cur_color.g, s.cur_color.b
            else:
                r, g, b = s.min_color.r, s.min_color.g, s.min_color.b

            self._draw(s.start, s.end, [r, g, b])
        self._iterations += 1

    def _draw(self, start: int, end: int, color: list[float]) -> None:
        for i in range(start, end + 1):
            self._screen[i].r = color[0]
            self._screen[i].g = color[1]
            self._screen[i].b = color[2]
