#!/usr/bin/env python3
from collections import defaultdict
from typing import Any, Dict, cast

from demo.config import CCKConfig, Config
from demo.doorSwitch import doorDemo
from demo.ir import DEFAULT_CONFIG as irDefaultConfig
from demo.ir import irDemo
from demo.motor import DEFAULT_CONFIG as pawDefaultConfig
from demo.motor import runMotorDemo
from demo.neopixel import DEFAULT_CONFIG as neopixelDefaultConfig
from demo.neopixel import runNeoPixelDemo
from presenter_drivers.logger.logger import create_logger

DEFAULT_CONFIG = {
    "cckConfig": {
        "cckDisplayConfig": neopixelDefaultConfig.get("cckDisplayConfig", {}),
        "pawConfig": pawDefaultConfig.get("pawConfig", {}),
        "irConfig": irDefaultConfig.get("irConfig", {}),
    }
}

logger = create_logger("HAMBoneDemo")

DEFAULT_DEMO = "neopixel"


def _runAllDemos(config: CCKConfig) -> None:
    logger.info("Running all dmeos")
    _runNeoPixelDemo(config)
    _runMotorDemo(config)
    _runIRDemo(config)


def _runNeoPixelDemo(config: CCKConfig) -> None:
    logger.info("Running display dmeo only")
    config["cckDisplayConfig"]["logger"] = logger
    runNeoPixelDemo(config["cckDisplayConfig"])


def _runMotorDemo(config: CCKConfig) -> None:
    logger.info("Running motor dmeo only")
    config["pawConfig"]["logger"] = logger
    runMotorDemo(config["pawConfig"])


def _runIRDemo(config: CCKConfig) -> None:
    logger.info("Running IR demo only")
    config["irConfig"]["logger"] = logger
    irDemo(config["irConfig"])


def _runDoorDemo(config: CCKConfig) -> None:
    logger.info("Running door demo only")
    config["doorConfig"]["logger"] = logger
    doorDemo(config["doorConfig"])


DEMOS = {
    "all": _runAllDemos,
    "display": _runNeoPixelDemo,
    "neopixel": _runNeoPixelDemo,
    "motor": _runMotorDemo,
    "ir": _runIRDemo,
    "door": _runDoorDemo,
}


def main(config: Config, demo: str) -> None:
    config = cast(
        Config, defaultdict(dict, {**DEFAULT_CONFIG, **cast(Dict[str, Any], config)})
    )  # Need to fix this for nesting
    logger.info("\n\nConfig: %s\n\n", config)

    DEMOS.get(demo, _runAllDemos)(config.get("cckConfig", {}))


if __name__ == "__main__":
    import argparse
    from json import decoder, load
    from sys import stdin

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        default=stdin,
        type=argparse.FileType("r"),
        nargs="?",
        help="The config file.",
    )

    parser.add_argument(
        "-d",
        "--demo",
        choices=DEMOS.keys(),
        default=DEFAULT_DEMO,
        help=f"Choose a demo to run. default ({DEFAULT_DEMO})",
    )

    args = parser.parse_args()

    try:
        main(load(args.config), args.demo)
    except decoder.JSONDecodeError:
        logger.warning("Unable to parse config file.")
