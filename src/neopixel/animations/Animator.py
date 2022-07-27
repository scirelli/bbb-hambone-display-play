from abc import ABC, abstractmethod


class Animator(ABC):
    @abstractmethod
    def animate(self, dt_ns: int) -> None:
        pass


class NullAnimator(Animator):
    pass


class FailAnimator(Animator):
    def animate(self, dt_ns: int) -> None:
        raise NotImplementedError()


class NotAnAnimator(Animator):
    def animate(self, dt_ns: int) -> None:
        raise LookupError()
