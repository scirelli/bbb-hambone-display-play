from abc import ABC, abstractmethod


class Animator(ABC):
    @abstractmethod
    def animate(self):
        pass


class NullAnimator(Animator):
    pass


class FailAnimator(Animator):
    def animate(self):
        raise NotImplementedError()


class NotAnAnimator(Animator):
    def animate(self):
        raise LookupError()
