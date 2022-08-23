#!/usr/bin/env python3
from time import sleep

from tabulate import tabulate

from hambone.sensors.CCKIR import CCKIR
from hambone.sensors.ir import MinMax as MinMaxCalibrator

cckir = CCKIR({})
calibrator = MinMaxCalibrator({"sensors": cckir.get_sensors()})
calibrator.start()
sleep(10)
results = calibrator.stop()
data = [(m, x, ((x - m) / x), (x - m)) for m, x in results]
print(tabulate(data, headers=["Raw Min", "Raw Max", "Ratio", "Diff"]))
