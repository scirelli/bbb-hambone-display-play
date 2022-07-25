from abc import ABC, abstractmethod


class Animator(ABC):
    @abstractmethod
    def animate(self):
        pass
