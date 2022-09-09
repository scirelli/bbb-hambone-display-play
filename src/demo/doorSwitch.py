#!/usr/bin/env python3
from collections import defaultdict
from logging import Logger
from time import sleep
from typing import Any, Dict, cast

from hambone.logger.logger import create_logger
from hambone.neopixel import writer
from hambone.neopixel.CCKDisplay import CCKDisplay
from hambone.sensors.CCKDoor import AccessDoorSwitch

from .config import Config, DoorConfig

DEFAULT_CONFIG = {
    "doorConfig": {
        "doorSwitchPin": "P8_8",
        "foreground": [0, 0, 20],
        "background": [0, 0, 0],
        "neoPixelPRUConfig": {
            "ledCount": 42,
            "writerConfig": {
                "type": "PRUDeviceWriter",
                "config": {
                    "_fileName": "/dev/rpmsg_pru30",
                    "fileName": "/tmp/rpmsg_pru30.txt",
                    "fileMode": "a",
                },
            },
            "writer": None,
        },
    },
}

logger = create_logger("DoorDemo")


def doorDemo(config: DoorConfig) -> None:  # pylint: disable = too-many-locals
    log: Logger = create_logger("DoorDemo")

    # Add a logger instance and the writer instance to the CCKDisplay config
    config["logger"] = log

    neoPixelConfig = config["neoPixelPRUConfig"]
    neoPixelConfig["logger"] = log
    writerConfig = neoPixelConfig.get("writerConfig", {})
    neoPixelConfig["writerConfig"] = writerConfig

    fg_color = config.get("foreground", [0, 0, 20])
    bg_color = config.get("background", [0, 0, 0])

    wr = writer.__dict__[writerConfig.get("type", "STDOutWriter")](
        writerConfig.get("config", {}).get("fileName", "")
    )

    with wr as f:
        neoPixelConfig["writer"] = f
        cckDisplay = CCKDisplay({"logger": log, "neoPixelPRUConfig": neoPixelConfig})
        cckDoor = AccessDoorSwitch(cast(AccessDoorSwitch.Config, config))

        print("Demo engaged\n")
        print("Press ctrl+c to exit door demo.")

        try:
            while True:
                if cckDoor.is_open():
                    cckDisplay.set_all_segments_color(*fg_color)
                else:
                    cckDisplay.set_all_segments_color(*bg_color)

                sleep(0.1)

        except KeyboardInterrupt:
            pass

        cckDisplay.all_segments_off()


def _main(config: Config) -> None:
    config = cast(
        Config, defaultdict(dict, {**DEFAULT_CONFIG, **cast(Dict[str, Any], config)})
    )  # Need to fix this for nesting
    logger.info("\n\nConfig: %s\n\n", config)

    cckConfig = config.get("cckConfig", {})
    cckConfig["doorConfig"]["logger"] = logger

    doorDemo(cckConfig["doorConfig"])


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
        logger.warning("Unable to parse config file.")
