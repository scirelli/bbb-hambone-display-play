#!/usr/bin/env python3
#  pylint: disable=wrong-import-order
import logging
from collections import defaultdict
from time import perf_counter_ns
from typing import Any, Dict

from neopixel import animations
from neopixel.display import NeoPixelDisplay
from neopixel.logger import create_logger
from neopixel.writer.PRUDeviceWriter import PRUDeviceWriter

logging.basicConfig(level=logging.DEBUG)

LED_COUNT = 42
DEFAULT_CONFIG = {
    "iterations": 1000,
    "PRU": {
        "file": "/tmp/pru_output.bin",
    },
    "animations": [
        {
            "type": "Rainbow",
            "config": {},
        },
    ],
}


def main(config: Dict[str, Any]) -> None:
    config = defaultdict(dict, {**DEFAULT_CONFIG, **config})
    iterations = int(config.get("iterations", 1000))
    loaded_animations: list[animations.Animator] = []
    start_time: int = perf_counter_ns()

    with PRUDeviceWriter(config.get("PRU", {}).get("file", "")) as f:
        display = NeoPixelDisplay(LED_COUNT, f)

        for a in config.get("animations", []):
            anim_config = a.get("config", {})
            anim_config["display"] = display
            loaded_animations.append(
                animations.__dict__.get(
                    a.get("type", "FailAnimator"), animations.FailAnimator
                )(anim_config)
            )

        for _ in range(iterations):
            start_time = perf_counter_ns()
            for a in loaded_animations:
                a.animate(perf_counter_ns() - start_time)
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
        main(load(args.config))
    except decoder.JSONDecodeError:
        logger.warning("Unable to parse config file.")
