from abc import ABC, abstractmethod


class HardwareController(ABC):
    @abstractmethod
    def read_pin(self, pin: int) -> int:
        pass

    @abstractmethod
    def write_pin(self, pin: int, state: int) -> None:
        pass

    @abstractmethod
    def read_named_pin(self, pin_name: str) -> int:
        pass

    @abstractmethod
    def write_named_pin(self, pin_name: str, state: int) -> None:
        pass
