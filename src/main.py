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
    "ledCount": 42,
    "iterations": -1,
    "totalSimulationTimeSeconds": 10,
    "PRU": {
        "file": "/tmp/pru_output.bin",
    },
    "animations": [
        {
            "type": "Rainbow",
            "totalAnimationTimeSeconds": -1,
            "config": {},
        },
    ],
}


def main(config: Dict[str, Any]) -> None:
    config = defaultdict(dict, {**DEFAULT_CONFIG, **config})
    iterations: int = int(config.get("iterations", -1))
    totalSimulationTimeSeconds: float = float(
        config.get("totalSimulationTimeSeconds", 10)
    )
    loaded_animations: list[dict[str, Any]] = []
    dt_ns: int = 0
    start_time_ns: int = 0
    currentTime: float = 0
    cnt: int = 0

    with PRUDeviceWriter(config.get("PRU", {}).get("file", "")) as f:
        display = NeoPixelDisplay(int(config.get("ledCount", LED_COUNT)), f)
        display.clear()
        display.draw()

        for a in config.get("animations", []):
            anim_config = a.get("config", {})
            anim_config["display"] = display
            anim_config["totalAnimationTimeSeconds"] = float(
                anim_config.get("totalAnimationTimeSeconds", totalSimulationTimeSeconds)
            )
            loaded_animations.append(
                {
                    "animation": animations.__dict__.get(
                        a.get("type", "FailAnimator"), animations.FailAnimator
                    )(anim_config),
                    "config": anim_config,
                }
            )

        while currentTime < totalSimulationTimeSeconds:
            start_time_ns = perf_counter_ns()
            for a in loaded_animations:
                if currentTime <= a["config"]["totalAnimationTimeSeconds"]:
                    a["animation"].animate(dt_ns)
            display.draw()
            cnt = cnt + 1
            if iterations != -1 and cnt >= iterations:
                break

            dt_ns = perf_counter_ns() - start_time_ns
            currentTime = currentTime + (dt_ns / 1e9)  # 1ns/1e9 s

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
