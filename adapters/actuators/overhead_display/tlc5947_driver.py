#!/usr/bin/env python

# Modded by Noah Vawter 2021 for Andy Cavatorta Studios
# SPDX-FileCopyrightText: 2018 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2018 Walter Haschka
# SPDX-License-Identifier: MIT

import board
import busio
import digitalio

import adafruit_tlc5947

class tlc_5947():
    def __init__( self, latch, driverCount ):

        self.driver_count = driverCount
        
        # Initialize SPI bus.
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)

        # Initialize TLC5947
        self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=driverCount)

        self.ledOut = []
        for idx in range( 0, 24 * self.driver_count ):
            print( idx )
            self.ledOut.append( self.tlc5947.create_pwm_out( idx ) )
            
        
        # You can optionally disable auto_write which allows you to control when
        # channel state is written to the chip.  Normally auto_write is true and
        # will automatically write out changes as soon as they happen to a channel, but
        # if you need more control or atomic updates of multiple channels then disable
        # and manually call write as shown below.
        # tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=driverCount, auto_write=False)

        # There are two ways to set channel PWM values. The first is by getting
        # a PWMOut object that acts like the built-in PWMOut and can be used anywhere
        # it is used in your code.  Change the duty_cycle property to a 16-bit value
        # (note this is NOT the 12-bit value supported by the chip natively) and the
        # PWM channel will be updated.

    def write( self, ledIdx, val ):
        self.ledOut[ ledIdx ].duty_cycle = val
        
