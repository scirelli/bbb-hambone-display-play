#!/usr/bin/env python
# pylint: disable=wrong-import-position unused-import wrong-import-order
# flake8: noqa E402
from curses import wrapper

import board
import busio

# ##############################################
# ADS11x5 Pins
# ADDR - I2C address selection pin
#    Default address is 0x48
#    The ADS11x5 chips have a base 7-bit I2C address of 0x48 (1001000) and a addressing scheme that allows different addresses using just one address pin (ADDR).
#    ┏━━━━━┯━━━━━┓
#    ┃ I2C │ADDR ┃
#    ┃ ADDR│Pin  ┃
#    ┠─────┼─────┨
#    ┃0x48 │GND  ┃
#    ┠─────┼─────┨
#    ┃0x49 │VIN  ┃
#    ┠─────┼─────┨
#    ┃0x4A │SDA  ┃
#    ┠─────┼─────┨
#    ┃0x4B │SCL  ┃
#    ┗━━━━━┷━━━━━┛

# ALRT           - Digital comparator output or conversion ready, can be set up and used for interrupt / asynchronous read.
# A+ and A-      - ADC power supply (VIN through a ferrite) and ADC ground (digital GND through a ferrite) these are OUTPUTs not inputs!
# A0, A1, A2, A3 - ADC input pins for each channel.

# Single Ended vs. Differential Inputs:
# The ADS1x15 breakouts support up to 4 Single Ended or 2 Differential inputs.
# Single Ended inputs measure the voltage between the analog input channel (A0-A3) and analog ground (GND).
# Differential inputs measure the voltage between two analog input channels.  (A0&A1 or A2&A3).
# Probe the I2C busses for connected devices:
# $ i2cdetect -y -r 0
# $ i2cdetect -y -r 1
# ##############################################
DEFAULT_I2C_ADDR = 0x48  # For the ADS11x5
A0_L_ADDR = DEFAULT_I2C_ADDR
A0_H_ADDR = DEFAULT_I2C_ADDR + 0x01

BOARD_1_ADDR = A0_L_ADDR
BOARD_2_ADDR = A0_H_ADDR
MAX = 0b111111111111

i2c = busio.I2C(board.SCL, board.SDA)

import adafruit_ads1x15.ads1015 as ADS  # isort:skip # noqa
from adafruit_ads1x15.analog_in import AnalogIn  # isort:skip # noqa

ads = ADS.ADS1015(i2c)

channels = [
    AnalogIn(ads, ADS.P0),
    AnalogIn(ads, ADS.P1),
    AnalogIn(ads, ADS.P2),
    AnalogIn(ads, ADS.P3),
]


def main(stdscr):
    while True:
        i = 0
        chan = channels[i]
        stdscr.addstr(
            i,
            0,
            f"Chan_{i} Value: {chan.value:.6f}, {chan.voltage:.6f}V, {(MAX/chan.value):.6f}",
        )

        i += 1
        chan = channels[i]
        stdscr.addstr(
            i,
            0,
            f"Chan_{i} Value: {chan.value:.6f}, {chan.voltage:.6f}V, {(MAX/chan.value):.6f}",
        )

        i += 1
        chan = channels[i]
        stdscr.addstr(
            i,
            0,
            f"Chan_{i} Value: {chan.value:.6f}, {chan.voltage:.6f}V, {(MAX/chan.value):.6f}",
        )

        i += 1
        chan = channels[i]
        stdscr.addstr(
            i,
            0,
            f"Chan_{i} Value: {chan.value:.6f}, {chan.voltage:.6f}V, {(MAX/chan.value):.6f}",
        )

        stdscr.refresh()


if __name__ == "__main__":
    wrapper(main)
