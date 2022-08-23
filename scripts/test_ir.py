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
    data.extend([((i + 1), m, x, ((x - m) / x), (x - m)) for m, x in results])
    sleep(2)

print(
    tabulate(
        data, headers=["Run", "Raw Min", "Raw Max", "Ratio", "Diff"], showindex="always"
    )
)
