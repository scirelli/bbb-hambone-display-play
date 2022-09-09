#!/usr/bin/env python3
from collections import defaultdict
from time import sleep
from typing import Any, Dict, cast

from hambone.logger.logger import create_logger
from hambone.motor.CCKPaw import CCKPaw

from .config import Config, PawConfig

DEFAULT_LOGGER = create_logger("MotorDemo")
DEFAULT_CONFIG = {
    "pawConfig": {
        "motorConfig": {
            "motorIN1Pin": "P8_7",
            "motorIN2Pin": "P8_9",
        },
        "motorLimitsConfig": {
            "frontLimitSwitchPin": "P8_12",
            "rearLimitSwitchPin": "P8_10",
        },
        "logger": DEFAULT_LOGGER,
    }
}


def runMotorDemo(config: PawConfig) -> None:
    logger = config.get("logger", DEFAULT_LOGGER)
    cckPaw: CCKPaw = CCKPaw(cast(CCKPaw.Config, config))
    logger.info("Resetting paw position to home position")
    cckPaw.reset()
    logger.info("Sleeping 10s")
    sleep(10)
    logger.info("Presentig a check")
    cckPaw.present()
    logger.info("Sleeping 10s")
    sleep(10)
    logger.info("Resetting paw position to home position")
    cckPaw.reset()


def _main(config: Config) -> None:
    logger = DEFAULT_LOGGER
    config = cast(
        Config, defaultdict(dict, {**DEFAULT_CONFIG, **cast(Dict[str, Any], config)})
    )  # Need to fix this for nesting
    logger.info("\n\nConfig: %s\n\n", config)

    pawConfig = config["cckConfig"]["pawConfig"]
    pawConfig["logger"] = logger

    runMotorDemo(pawConfig)


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

    args = parser.parse_args()

    try:
        _main(load(args.config))
    except decoder.JSONDecodeError:
        DEFAULT_LOGGER.warning("Unable to parse config file.")
