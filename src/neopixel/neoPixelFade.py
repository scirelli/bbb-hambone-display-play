#!/usr/bin/env python3
from time import sleep
import math
#################
# Fade HAMBone display from full on to 0 in 0.25s
#
#
#################
FADE_TIME_S = 0.25
FULL_INTENSITY = 128
FADE_STEP_TIME_S = FADE_TIME_S / FULL_INTENSITY

x = 0
for i in range(365):
    x = i
    y = 128*(1-(math.sin(x/365*math.pi/2)))
    print(f"{math.ceil(y)}")
    sleep(FADE_STEP_TIME_S)
