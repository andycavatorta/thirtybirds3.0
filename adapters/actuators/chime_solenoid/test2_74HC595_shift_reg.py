#!/usr/bin/env python

import time
import math
import HC595_shift_reg

shift_register = HC595_shift_reg.HC595()


sequence = [
    [1,0,0,0,0],
    [0,0,1,0,0],
    [1,0,0,0,0],
    [0,0,1,0,0],
    [1,0,0,0,0],
    [0,0,0,1,0],
    [1,0,0,0,0],
    [0,0,0,1,0],
    [0,1,0,0,0],
    [0,0,0,1,0],
    [0,1,0,0,0],
    [0,0,0,1,0],
    [0,1,0,0,0],
    [0,0,0,0,1],
    [0,1,0,0,0],
    [0,0,0,0,1],
    [0,0,1,0,0],
    [0,0,0,0,1],
    [0,0,1,0,0],
    [0,0,0,0,1],
    [0,0,1,0,0],
    [1,0,0,0,0],
    [0,0,1,0,0],
    [1,0,0,0,0],
    [0,0,0,1,0],
    [1,0,0,0,0],
    [0,0,0,1,0],
    [1,0,0,0,0],
    [0,0,0,1,0],
    [0,1,0,0,0],
    [0,0,0,1,0],
    [0,1,0,0,0],
    [0,0,0,0,1],
    [0,1,0,0,0],
    [0,0,0,0,1],
    [0,1,0,0,0],
    [0,0,0,0,1],
    [0,0,1,0,0],
    [0,0,0,0,1],
    [0,0,1,0,0]
]

seq_step = 0
val = [ 0 ]
period = 0.8

try:
    ontime = 0.0100
    offtime = period - ontime
    while True:
        for beat in sequence:
            val[ 0 ] = 0;
            for channel_number in range( 0, 5 ):
                if beat[channel_number] == 1:
                    val[ 0 ] = val[ 0 ] + ( 1 << channel_number )
            
            shift_register.write( val )
            time.sleep( ontime )
            
            #val[ 0 ] = 0x00
            #shift_register.write( val )
            time.sleep( offtime )

except KeyboardInterrupt:       
    print( "You've exited the program." )

finally:
    print( "cleaning up GPIO now." )
    shift_register.disable_Output_Enable()    
    
    
    
    
    





