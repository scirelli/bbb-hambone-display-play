#!/usr/bin/env python3
#  pylint: disable=wrong-import-order
import logging
from collections import defaultdict
from typing import Any, Dict

from neopixel.animations.fades.rainbow import Rainbow
from neopixel.display import NeoPixelDisplay
from neopixel.logger import create_logger
from neopixel.writer.PRUDeviceWriter import PRUDeviceWriter

logging.basicConfig(level=logging.DEBUG)

LED_COUNT = 42
DEFAULT_CONFIG = {
    'iterations': 1000,
    'PRU': {
        'file': "/tmp/pru_output.bin",
    },
    'animations': [
        {
            'type': 'Rainbow',
            'config': {
            },
        },
    ],
}


def main(config: Dict[str, Any]) -> None:
    config = defaultdict(dict, {**DEFAULT_CONFIG, **config})
    iterations = int(config.get('iterations', 1000))

    with PRUDeviceWriter(config.get('PRU', {}).get('file', '')) as f:
        display = NeoPixelDisplay(LED_COUNT, f)
        a = Rainbow(display)

        for _ in range(iterations):
            a.animate()
            display.draw()

        display.clear()
        display.draw()


if __name__ == "__main__":
    import argparse
    from json import decoder, load
    from sys import stdin

    parser = argparse.ArgumentParser()
    logger = create_logger("HAMBone")

    parser.add_argument(
        "--config",
        default=stdin,
        type=argparse.FileType("r"),
        nargs="?",
        help="The config file.",
    )

    args = parser.parse_args()

    try:
        logger.debug(main(load(args.config)))
    except decoder.JSONDecodeError:
        logger.warning("Unable to parse config file.")
