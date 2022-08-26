#!/usr/bin/env python3
#  pylint: disable=wrong-import-order
from collections import defaultdict
from logging import Logger
from time import sleep
from typing import Any, Tuple, cast

from tabulate import tabulate

from hambone.logger.logger import create_logger
from hambone.motor.CCKPaw import CCKPaw
from hambone.neopixel import writer
from hambone.neopixel.CCKDisplay import CCKDisplay
from hambone.neopixel.Demo import Demo as NeoPixelDemo
from hambone.neopixel.NeoPixelPRU import NeoPixelPRU
from hambone.sensors.CCKIR import CCKIR
from hambone.sensors.ir import MinMax

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
        "irConfig": {
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
    },
    "demo": {"which": "all"},
}

logger = create_logger("HAMBoneDemo")


def main(config: dict[str, Any]) -> None:
    config = defaultdict(
        dict, {**DEFAULT_CONFIG, **config}
    )  # Need to fix this for nesting
    logger.info("\n\nConfig: %s\n\n", config)

    demoConfig = config.get("demo", {})
    cckConfig = config.get("cckConfig", {})
    cckConfig["pawConfig"]["logger"] = logger
    cckConfig["displayConfig"]["logger"] = logger
    cckConfig["irConfig"]["logger"] = logger

    match demoConfig.get("which", "all"):
        case "display":
            logger.info("Running display dmeo only")
            runNeoPixelDemo(cckConfig["displayConfig"])
        case "motor":
            logger.info("Running motor dmeo only")
            runMotorDemo(cckConfig["pawConfig"])
        case "ir":
            logger.info("Running IR demo only")
            irDemo(cckConfig["irConfig"])
        case _:
            logger.info("Running all dmeos")
            runNeoPixelDemo(cckConfig["displayConfig"])
            runMotorDemo(cckConfig["pawConfig"])


def runNeoPixelDemo(config: dict[str, Any]) -> None:
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


def runMotorDemo(config: dict[str, Any]) -> None:
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


def irDemo(config: dict[str, Any]) -> None:
    log: Logger = create_logger("IRDemo")

    # Add a logger instance and the writer instance to the CCKDisplay config
    config["logger"] = log
    neoPixelConfig = config["neoPixelConfig"]
    neoPixelConfig["logger"] = log
    writerConfig = neoPixelConfig.get("writerConfig", {})
    neoPixelConfig["writerConfig"] = writerConfig

    wr = writer.__dict__[writerConfig.get("type", "STDOutWriter")](
        writerConfig.get("config", {}).get("fileName", "")
    )

    lights = [
        16,  # LEFT_FRONT
        6,  # LEFT_MIDDLE
        0,  # LEFT_REAR
        41,  # RIGHT_FRONT = 3
        15,  # RIGHT_MIDDLE = 4
        5,  # RIGHT_REAR = 5
    ]

    print("Press ctrl+c to exit IR demo.")
    try:
        with wr as f:
            neoPixelConfig["writer"] = f
            neopixel_controller: NeoPixelPRU = NeoPixelPRU(
                cast(NeoPixelPRU.Config, neoPixelConfig)
            )
            cckIR = CCKIR(cast(CCKIR.Config, config))

            calibrator = MinMax({"sensors": cckIR.get_sensors()})
            input(
                "\n\nPress enter when ready to calibrate. Remember to move paper around.\n"
            )
            calibrator.start()
            sleep(20)
            minMaxes = calibrator.stop()
            log.debug(_ir_calibration_results_to_string(minMaxes))
            midPoints = [v[0] + ((v[1] - v[0]) / 2) for v in minMaxes]
            input("\n\nCalibration complete. Press a key to run demo.")
            while True:
                for sensor in CCKIR.Sensor:
                    if cckIR.read_sensor(sensor) > midPoints[sensor.value]:
                        log.info("Under %s", sensor.name)
                        neopixel_controller.set_color(lights[sensor.value], 0, 128, 0)
                    else:
                        neopixel_controller.set_color(lights[sensor.value], 0, 0, 0)
    except KeyboardInterrupt:
        pass


def _ir_calibration_results_to_string(results: Tuple[Tuple[int, int], ...]) -> str:
    data = []
    for i in range(len(results)):
        data.extend(
            [
                (
                    (i + 1),
                    CCKIR.Sensor(sensor).name,
                    v[0],
                    v[0] + ((v[1] - v[0]) / 2),
                    v[1],
                    f"{((abs(v[0] - v[1]) / ((v[0] + v[1]) / 2)) * 100):.2f}%",
                    (v[1] - v[0]),
                )
                for sensor, v in enumerate(results)
            ]
        )

    return tabulate(data, headers=["Name", "Min", "Mid", "Max", "% Diff", "Diff"])


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
