#!/usr/bin/env python

import time
import math

import HC595_shift_reg as shifter

reg = shifter.HC595()


# attraction mode
seq = [ [ 1, 0, 0, 0,  0, ],
        [ 0, 1, 0, 0,  0, ],
        [ 0, 0, 1, 0,  0, ],
        [ 0, 0, 0, 1,  0, ],
        [ 0, 0, 0, 0,  1  ] ]
"""
# score
seq = [ [ 1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 1, 0, 0,  0, 1, 0, 0,  0, 1, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 1, 0,  0, 0, 1, 0,  0, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 1,  0, 0, 0, 1,  0, 0, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0 ] ]


seq = [ [ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 1, 0, 0, 0,  0, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 1, 0, 0, 0,  0, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 1, 0, 0,  0, 0, 0, 0,  0, 1, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ] ]

seq = [ [ 1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 1, 0 ],
        [ 0, 0, 1, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 1, 0, 1 ],
        [ 1, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0 ],
        [ 1, 0, 0, 1,  0, 0, 1, 0,  1, 0, 0, 1,  0, 0, 1, 0 ] ]

seq = [ [ 1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 1, 0 ],
        [ 0, 0, 1, 0,  0, 0, 1, 0,  0, 0, 1, 0,  0, 1, 0, 1 ],
        [ 1, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  1, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 1, 0,  0, 0, 0, 0,  0, 0, 1, 1 ] ]
        
seq = [ [ 1, 0, 0, 0,  0, 0, 0, 0  ],
        [ 0, 1, 0, 0,  0, 0, 0, 0  ],
        [ 0, 0, 1, 0,  0, 0, 0, 0  ],
        [ 0, 0, 0, 1,  0, 0, 0, 0  ],
        [ 0, 0, 0, 0,  1, 0, 0, 0  ] ]

"""
#seq = [ 1, 0, 0, 0, 1, 0, 0, 0,  1, 0, 1, 0, 1, 0, 1, 0,  1, 0, 0, 1, 0, 0, 1, 0,   1, 0, 0, 1, 0, 0, 1, 1 ]
seq_step = 0

val = [ 0 ]
lfo = 3.141596

period = 0.1
period = 1.1

# this is put inside a try block so it can clean up 
# the output enable.  very important to protect relays from
# being left on!!!!
try:
    while True:
        print()        
        
        ontime =2.09
        offtime = 2.0
    
        val[ 0 ] = 0;
        for trk in range( 0, 5 ):
            if seq[ trk ][ seq_step ] == 1:    
                val[ 0 ] = val[ 0 ] + ( 1 << trk )

        #print( ontime, offtime )    
        reg.write( val )
        print( val )
        time.sleep( ontime )

        val[ 0 ] = 0x00
        reg.write( val )
        print( val )
        time.sleep( offtime )

        seq_step = seq_step + 1
        if seq_step >= 5:
            seq_step = 0

except KeyboardInterrupt:       
    print( "You've exited the program." )

finally:
    print( "cleaning up GPIO now." )
    reg.disable_Output_Enable()    
    
    
    
    
    





