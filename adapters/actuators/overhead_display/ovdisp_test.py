#!/usr/bin/env python

# adafruit libs
import board
import digitalio

import tlc5947_driver as td


def up_n_down( ledIdx ):
    step = 3000
    start_pwm = 0
    end_pwm = 65535  # 50% (32767, or half of the maximum 65535):

    print("up")
    for pwmVal in range(start_pwm, end_pwm, step):
        print( pwmVal )
        ovdisp.write( ledIdx, pwmVal )
        # tlc5947.write()        # see NOTE below

    print("down")
    for pwmVal in range(end_pwm, start_pwm, 0 - step):
        print( pwmVal )
        ovdisp.write( ledIdx, pwmVal )
        # tlc5947.write()        # see NOTE below

    # NOTE: if auto_write was disabled you need to call write on the parent to
    # make sure the value is written in each loop (this is not common, if disabling
    # auto_write you probably want to use the direct 12-bit raw access instead,
    # shown next).



def back_n_forth():
    while True:
        up_n_down( 0 )
        up_n_down( 24 )
        up_n_down( 48 )
        up_n_down( 72 )
        up_n_down( 48 )
        up_n_down( 24 )

# initialize overhead display
ovdisp = td.tlc_5947(  digitalio.DigitalInOut( board.D5 ), driverCount = 4 )

back_n_forth()
    


