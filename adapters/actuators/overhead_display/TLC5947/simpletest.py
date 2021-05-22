# SPDX-FileCopyrightText: 2018 Tony DiCola for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of controlling the TLC5947 12-bit 24-channel PWM controller.
# Will update channel values to different PWM duty cycles.
# Author: Tony DiCola

import board
import busio
import digitalio

import adafruit_tlc5947

# Define pins connected to the TLC5947
SCK = board.SCK
MOSI = board.MOSI
LATCH = digitalio.DigitalInOut(board.D5)

# Initialize SPI bus.
spi = busio.SPI(clock=SCK, MOSI=MOSI)

# Initialize TLC5947
tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH)

red = tlc5947.create_pwm_out(0)
green = tlc5947.create_pwm_out(21)
blue = tlc5947.create_pwm_out(2)

step = 120
start_pwm = 0
end_pwm = 32767  # 50% (32767, or half of the maximum 65535):

while True:
    for pin in (red, green, blue):
        # Brighten:
        print("Brightening LED")
        for pwm in range(start_pwm, end_pwm, step):
            pin.duty_cycle = pwm

        # Dim:
        print("Dimming LED")
        for pwm in range(end_pwm, start_pwm, 0 - step):
            pin.duty_cycle = pwm

# Note if auto_write was disabled you need to call write on the parent to
# make sure the value is written (this is not common, if disabling auto_write
# you probably want to use the direct 12-bit raw access instead shown below).
#            tlc5947.write()

# The other way to read and write channels is directly with each channel 12-bit
# value and an item accessor syntax.  Index into the TLC5947 with the channel
# number (0-23) and get or set its 12-bit value (0-4095).
# For example set channel 1 to 50% duty cycle.
# tlc5947[1] = 2048
# Or set channel 23 (first channel from the end) to 2/3 duty cycle.
# tlc5947[-1] = 2730
# Again be sure to call write if you disabled auto_write.
# tlc5947.write()