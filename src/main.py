#!/usr/bin/env python3
#  pylint: disable=wrong-import-order
from collections import defaultdict
from logging import Logger
from time import sleep
from typing import Any, Dict, cast

from hambone.logger.logger import create_logger
from hambone.motor.CCKPaw import CCKPaw
from hambone.neopixel import writer
from hambone.neopixel.CCKDisplay import CCKDisplay
from hambone.neopixel.Demo import Demo as NeoPixelDemo

TWO_SECONDS = 2
FIVE_SECONDS = 5
TEN_SECONDS = 10
TOTAL_FLASH_TIME = TEN_SECONDS
TOTAL_ANIMATION_TIME = TEN_SECONDS

DEFAULT_CONFIG = {
    "cckConfig": {
        "displayConfig": {
            "neoPixelConfig": {
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
        "pawConfig": {
            "motorConfig": {
                "motorIN1Pin": "P8_7",
                "motorIN2Pin": "P8_9",
            },
            "motorLimitsConfig": {
                "frontLimitSwitchPin": "P8_12",
                "rearLimitSwitchPin": "P8_10",
            },
        },
    },
    "demo": {"which": "all"},
}

logger = create_logger("HAMBoneDemo")


def main(config: Dict[str, Any]) -> None:
    config = defaultdict(
        dict, {**DEFAULT_CONFIG, **config}
    )  # Need to fix this for nesting
    logger.info("\n\nConfig: %s\n\n", config)

    demoConfig = config.get("demo", {})
    cckConfig = config.get("cckConfig", {})
    cckConfig["pawConfig"]["logger"] = logger
    cckConfig["displayConfig"]["logger"] = logger

    match demoConfig.get("which", "all"):
        case "display":
            logger.info("Running display dmeo only")
            runNeoPixelDemo(cckConfig["displayConfig"])
        case "motor":
            logger.info("Running motor dmeo only")
            runMotorDemo(cckConfig["pawConfig"])
        case _:
            logger.info("Running all dmeos")
            runNeoPixelDemo(cckConfig["displayConfig"])
            runMotorDemo(cckConfig["pawConfig"])


def runNeoPixelDemo(config: Dict[str, Any]) -> None:
    log: Logger = create_logger("NeoPixelDemo")

    # Add a logger instance and the writer instance to the CCKDisplay config
    config["logger"] = log
    neoPixelConfig = config["neoPixelConfig"]
    neoPixelConfig["logger"] = log
    writerConfig = neoPixelConfig.get("writerConfig", {})
    neoPixelConfig["writerConfig"] = writerConfig

    wr = writer.__dict__[writerConfig.get("type", "STDOutWriter")](
        writerConfig.get("config", {}).get("fileName", "")
    )
    testNo = 0

    # Create the writer here so file can be closed when demo ends
    with wr as f:
        neoPixelConfig["writer"] = f
        cck = CCKDisplay(config)
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


def runMotorDemo(config: Dict[str, Any]) -> None:
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
        main(load(args.config))
    except decoder.JSONDecodeError:
        logger.warning("Unable to parse config file.")
