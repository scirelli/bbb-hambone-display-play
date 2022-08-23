#!/usr/bin/env python3
from time import sleep

from hambone.sensors.CCKIR import CCKIR
from hambone.sensors.ir import MinMax as MinMaxCalibrator

cckir = CCKIR({})
calibrator = MinMaxCalibrator({"sensors": cckir.get_sensors()})
calibrator.start()
sleep(30)
print(calibrator.stop())
