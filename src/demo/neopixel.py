#!/usr/bin/env python3
from collections import defaultdict
from logging import Logger
from time import sleep
from typing import Any, cast

from hambone.logger.logger import create_logger
from hambone.neopixel import writer
from hambone.neopixel.CCKDisplay import CCKDisplay

from .config import CCKDisplayConfig, Config
from .neopixelDemo import Demo as NeoPixelDemo

TWO_SECONDS = 2
FIVE_SECONDS = 5
TEN_SECONDS = 10
TOTAL_FLASH_TIME = TEN_SECONDS
TOTAL_ANIMATION_TIME = TEN_SECONDS


DEFAULT_LOGGER = create_logger("NeoPixelDemo")
DEFAULT_CONFIG = {
    "cckDisplayConfig": {
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
        "logger": DEFAULT_LOGGER,
    },
}
log: Logger = DEFAULT_LOGGER


def runNeoPixelDemo(config: CCKDisplayConfig) -> None:
    writerConfig = config.get("neoPixelPRUConfig", {}).get("writerConfig", {})

    wr = writer.__dict__[writerConfig.get("type", "STDOutWriter")](
        writerConfig.get("config", {}).get("fileName", "")
    )
    testNo = 0

    # Create the writer here so file can be closed when demo ends
    with wr as f:
        config["neoPixelPRUConfig"]["writer"] = f
        cck = CCKDisplay(cast(CCKDisplay.Config, config))
        demo = NeoPixelDemo(cck)

        log.info("Init")
        cck.all_segments_off()
        sleep(TWO_SECONDS)

        log.info("ATMOF-2159 Demo #%s\n\tAll display segments off.", testNo)
        cck.all_segments_off()
        sleep(TWO_SECONDS)
        testNo += 1

        log.info("ATMOF-2159 Demo #%d", testNo)
        log.info("\tAll display segments flashing red.")
        demo.all_Error_Flashing(TOTAL_FLASH_TIME * 1000)
        testNo += 1

        log.info("ATMOF-2159 Demo #%d", testNo)
        log.info("\tDisplay segment flashing green.")
        demo.display_flashing(0, 255, 0, TOTAL_FLASH_TIME * 1000)
        testNo += 1

        log.info("ATMOF-2159 Demo #%d", testNo)
        log.info("\tScanner segment flashing green.")
        demo.scanner_flashing(0, 255, 0, TOTAL_FLASH_TIME * 1000)
        testNo += 1

        log.info("ATMOF-2159 Demo #%d", testNo)
        log.info("\tPresenter segment flashing green.")
        demo.presenter_flashing(0, 255, 0, TOTAL_FLASH_TIME * 1000)
        testNo += 1

        log.info("ATMOF-2159 Demo #%d", testNo)
        log.info(
            "\tPresenter segment flashing yellow one second intervals. One second intervals is the default for flashing anyway."
        )
        demo.presenter_flashing(128, 128, 0, TOTAL_FLASH_TIME * 1000)
        testNo += 1

        log.info("ATMOF-2159 Demo #%d", testNo)
        log.info(
            "\tAnimation from all green to yellow to red as CCK counts down from 10s to retract check."
        )
        demo.check_retract_timer(TOTAL_ANIMATION_TIME * 1000)
        testNo += 1

        log.info("Clean up.")
        cck.all_segments_off()


def _main(config: Config) -> None:
    config = cast(
        Config,
        defaultdict(dict, {**DEFAULT_CONFIG, **cast(dict[str, Any], config)}),
    )  # Need to fix this for nesting
    log.info("\n\nConfig: %s\n\n", config)

    runNeoPixelDemo(config["cckConfig"]["cckDisplayConfig"])


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
        log.warning("Unable to parse config file.")
