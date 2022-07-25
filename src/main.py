#!/usr/bin/env python3
import logging

from neopixel.animations.fades.rainbow import Rainbow
from neopixel.display import NeoPixelDisplay
from neopixel.writer.PRUDeviceWriter import PRUDeviceWriter

logging.basicConfig(level=logging.DEBUG)

LED_COUNT = 42


def main() -> None:
    with PRUDeviceWriter("/tmp/pru_output.bin") as f:
        display = NeoPixelDisplay(LED_COUNT, f)
        a = Rainbow(display)

        for _ in range(1000):
            a.animate()
            display.draw()


if __name__ == "__main__":
    main()
