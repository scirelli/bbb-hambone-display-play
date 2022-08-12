from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import Logger
from time import perf_counter_ns
from typing import Any, Type

from ..logger.logger import create_logger
from .driver import MotorDriver, MotorLimits

DEFAULT_LOGGER = create_logger("CCKPaw")

# TODO: Add in IR sensors
# TODO: Door switch


class CCKException(Exception):
    pass


class MotorTimeout(CCKException):
    pass


class UnknownBreaker(CCKException):
    pass


class Breaker(ABC):
    @abstractmethod
    def shouldBreak(self) -> bool:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass


class NullBreaker(Breaker):
    def shouldBreak(self) -> bool:
        return True

    def cleanup(self) -> None:
        pass


class ErrorBreaker(Breaker):
    def shouldBreak(self) -> bool:
        raise CCKException("Error")

    def cleanup(self) -> None:
        pass


@dataclass
class LimitSwitch(NullBreaker):
    name: str


class TimeExpired(ErrorBreaker):
    MILLISECOND_IN_NANOSECOND = 1000000

    def __init__(self, totalTimeMs: int):
        self._totalTimeNs: int = totalTimeMs * TimeExpired.MILLISECOND_IN_NANOSECOND
        self._time = 0

    def shouldBreak(self) -> bool:
        if self._time == 0:
            self._time = perf_counter_ns()

        if (perf_counter_ns() - self._time) >= self._totalTimeNs:
            self._reset()
            raise MotorTimeout("Motor took to long to reach limit")

        return False

    def cleanup(self) -> None:
        self._reset()

    def _reset(self) -> None:
        self._time = 0


def breakerFactory(typ: str, arguments: dict[str, Any]) -> Breaker:
    f: dict[str, Type[Breaker]] = {
        "TimeExpired": TimeExpired,
        "LimitSwitch": LimitSwitch,
        "NullBreaker": NullBreaker,
        "ErrorBreaker": ErrorBreaker,
    }
    return f.get(typ, NullBreaker)(**arguments)


class CCKPaw:
    MAX_MOTOR_RUN_TIME_MS: int = 1400

    def __init__(self, config: dict[str, Any]):
        self._motor = MotorDriver(config.get("motorConfig", {}))
        self._limits = MotorLimits(config.get("motorLimitsConfig", {}))
        self._logger: Logger = config.get("logger", DEFAULT_LOGGER)
        self._motorBreakChecks: dict[str, list[Breaker]] = {
            "present": [],
            "retract": [],
        }

        for c in config.get("breakers", []):
            self._logger.info("Registering breaker %", c)
            self.registerBreaker(
                c["breakerFor"], breakerFactory(c["type"], c["arguments"])
            )

        # self.registerBreaker("present", TimeExpired(CCKPaw.MAX_MOTOR_RUN_TIME_MS))
        # self.registerBreaker("retract", TimeExpired(CCKPaw.MAX_MOTOR_RUN_TIME_MS))

    def reset(self) -> CCKPaw:
        return self.retract()

    def retract(self) -> CCKPaw:
        self._motor.backward()
        self._wait_for_any_limit_and_stop(self._motorBreakChecks["retract"])
        self._back_off_rear_limit()
        return self

    def present(self) -> CCKPaw:
        self._motor.forward()
        self._wait_for_any_limit_and_stop(self._motorBreakChecks["present"])
        self._back_off_front_limit()
        return self

    def registerBreaker(self, breaker_type: str, b: Breaker) -> CCKPaw:
        if breaker_type in self._motorBreakChecks:
            self._motorBreakChecks[breaker_type].append(b)
        else:
            raise UnknownBreaker(breaker_type)

        return self

    def unregisterBreaker(self, b: Breaker) -> CCKPaw:
        for lst in self._motorBreakChecks.values():
            if b in lst:
                lst.remove(b)

        return self

    def _wait_for_any_limit_and_stop(self, breakers: list[Breaker]) -> Breaker:
        while (
            not self._limits.is_front_limit_pressed()
            and not self._limits.is_rear_limit_pressed()
        ):
            motorState = self._motor.get_state()
            # Stop the motor before executing user code. This also stops the motor incase an exceptions get raised.
            self._motor.stop()
            for brk in breakers:
                try:
                    if (
                        brk.shouldBreak()
                    ):  # These functions should exectute as fast as possible so as to not stutter the motor's movement
                        return brk
                except Exception:
                    self._breakerCleanup(breakers)
                    raise

            self._motor.set_state(motorState)

        self._motor.stop()
        return LimitSwitch("front" if self._limits.is_front_limit_pressed() else "rear")

    def _back_off_front_limit(self) -> CCKPaw:
        self._motor.stop()
        self._motor.backward()

        while (
            self._limits.is_front_limit_pressed()
            and not self._limits.is_rear_limit_pressed()
        ):
            pass

        self._motor.stop()
        return self

    def _back_off_rear_limit(self) -> CCKPaw:
        self._motor.stop()
        self._motor.forward()

        while (
            self._limits.is_rear_limit_pressed()
            and not self._limits.is_front_limit_pressed()
        ):
            pass

        self._motor.stop()
        return self

    def _breakerCleanup(self, breakers: list[Breaker]) -> CCKPaw:
        for brk in breakers:
            brk.cleanup()
        return self
