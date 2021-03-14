#!/usr/bin/env python

import time
import math

import direct_GPIO as solenoid_driver
#import HC595_shift_reg as shifter

chimes = solenoid_driver.gpio_based( chimeGPIOs = [ 8, 12, 13, 14, 15 ] )
#reg = shifter.HC595()


# attraction mode
seq = [ [ 1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0 ],
        [ 0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1 ],
        [ 0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0 ] ]
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


lfo = 0 # initial phase of lfo, tyically statr quiet

BPM = 66  # set this
period = 60 / BPM # let this get computed

# this is put inside a try block so it can clean up 
# the output enable.  very important to protect relays from
# being left on!!!!
try:
    while True:
        lfo = lfo + .17
        mag = 0.5 + 0.5 * math.cos( lfo ) # leave this LFO output to always range from 0.0 to 1.0
        print( mag )
        ontime = 0.004 + 0.007 * mag
        ontime = 0.100 + 0.100 * mag   # shortest and longest ontimes.  this is in seconds.  e.g. 0.10  = 100 millisec
        offtime = period - ontime     # auto-calc offtime to maintain BPM as specified above
        print( ontime, offtime )    
    
        # turn em on from seq array
        chime_vec = []
        for trk in range( 0, 5 ):
            chime_vec.append( seq[ trk ][ seq_step ] )
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( ontime )
        
        # turn em off
        chime_vec = [ 0, 0, 0, 0, 0 ]
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( offtime )

        seq_step = seq_step + 1
        if seq_step >= 40:
            seq_step = 0

except KeyboardInterrupt:       
    print( "You've exited the program." )

finally:
    print( "cleaning up GPIO now." )
    chimes.disable_GPIOs()    
    
    
    
    
    





