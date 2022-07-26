from abc import ABC, abstractmethod


class Animator(ABC):
    @abstractmethod
    def animate(self) -> None:
        pass


class NullAnimator(Animator):
    pass


class FailAnimator(Animator):
    def animate(self) -> None:
        raise NotImplementedError()


class NotAnAnimator(Animator):
    def animate(self) -> None:
        raise LookupError()
