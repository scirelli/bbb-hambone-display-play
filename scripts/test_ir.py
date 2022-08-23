#!/usr/bin/env python3
from time import sleep

from tabulate import tabulate

from hambone.sensors.CCKIR import CCKIR
from hambone.sensors.ir import MinMax as MinMaxCalibrator

cckir = CCKIR({})
calibrator = MinMaxCalibrator({"sensors": cckir.get_sensors()})
data = []

for i in range(5):
    calibrator.start()
    sleep(10)
    results = calibrator.stop()
    data.extend(
        [
            (
                (i + 1),
                CCKIR.SensorIndex(sensor).name,
                v[0],
                v[1],
                f"{(((v[1] - v[0]) / v[1]) * 100):.2}%",
                (v[1] - v[0]),
            )
            for sensor, v in enumerate(results)
        ]
    )
    data.extend([[""] * 6])
    sleep(2)

print(tabulate(data, headers=["Run", "Name", "Min", "Max", "Ratio", "Diff"]))
