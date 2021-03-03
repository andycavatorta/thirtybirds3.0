#!/usr/bin/env python

import time
from enum import IntEnum

import RPi.GPIO as GPIO
import AMT203_absolute_encoder as encoder


def gpio_reset( pin_num ):
    print( "initin' ", pin_num )
    GPIO.setup( pin_num, GPIO.OUT)
    GPIO.output( pin_num, GPIO.HIGH)

def silly_but_vital_gpio_init():
    for chipSel in ChipSelects:
        gpio_reset( chipSel )
    return
    
    #gpio_reset(  8 )
    #gpio_reset(  7 )
    #gpio_reset( 18 )
    #gpio_reset( 17 )
    #gpio_reset( 16 )
    #gpio_reset(  5 )

# Chip selects used in Individual, Money and Society, 3/2021 aka 5 player pinball
class ChipSelects( IntEnum ):
    MOT1 =  8
    MOT2 =  7
    MOT3 = 18
    MOT4 = 17
    MOT5 = 16
    MOT6 =  5

# initialize all chip selects to unasserted in case program operation was interrupted
GPIO.setmode(GPIO.BCM)
silly_but_vital_gpio_init()

amt = encoder.AMT203( cs = ChipSelects.MOT6 )

amt.clean_buffer()


while True:
    pos = amt.get_position()
    print( pos )
    time.sleep( .1 )
    





