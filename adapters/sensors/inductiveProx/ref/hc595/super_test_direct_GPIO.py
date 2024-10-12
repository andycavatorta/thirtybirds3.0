#!/usr/bin/env python

"""
Test program to see what RPi GPIOs are available without complication from other peripherals.
Accompanying spreadsheet found at:
https://docs.google.com/spreadsheets/d/1GQxdGP54ufq57P0pmohJEUkQ9lBeoAXwtmMl0PQ5IR8/edit#gid=0
"""


import time
import math

import super_direct_GPIO as solenoid_driver

chimes = solenoid_driver.gpio_based( chimeGPIOs = [ 2, 3, 4, 17, 18,   27, 22, 23, 24, 10,   9, 25, 11, 8, 0,   1, 5, 6, 12, 13,   19, 16, 26, 20, 21 ] )


# attraction mode
seq = [ [ 1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0 ],
        [ 0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1 ],
        [ 0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0 ] ]

seq_step = 0

lfo = 0 # initial phase of lfo, tyically statr quiet
lfo2 = 0

#BPM = 96  # set this
#BPM = 566  # super fast mode
#period = 60 / BPM # let this get computed

# this is put inside a try block so it can clean up 
# the output enable.  very important to protect relays from
# being left on!!!!
try:
    while True:
        # compute LFOs
        lfo = lfo + 0.13
        lfo2 = lfo2 + 0.21
        mag = 0.5 + 0.5 * math.sin( lfo ) # leave this LFO output to always range from 0.0 to 1.0
        mag2 = 0.5 + 0.5 * math.sin( lfo2 )
        print( mag )

        BPM = 80 + 86 * mag2
        BPM = 80
        period = 60 / BPM
        
        # compute ontime
        # these are in seconds.  e.g. 0.10  = 100 millisec
        #ontime = 0.004 + 0.007 * mag   # very subtle cross over hardest part
        ontime = 0.010
        #ontime = 0.100 + 0.100 * mag   # pretty hard 10ms is ideal
        #ontime = 0.006 + 0.006 * mag   # should be pretty optimal
        #ontime = period / 2 # good for testing  to see on scope
        offtime = period - ontime     # auto-calc offtime to maintain BPM as specified above
        print( ontime, offtime )    

    
        # turn em on from seq array
        chime_vec = []
        for trk in range( 0, 25 ):
            if seq_step == trk:
                chime_vec.append( 1 )
            else:
                chime_vec.append( 0 )
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( ontime )
        
        # turn em off
        chime_vec = 25 * [ 0 ]
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( offtime )

        seq_step = seq_step + 1
        if seq_step >= 25:
            seq_step = 0

except KeyboardInterrupt:       
    print( "You've exited the program." )

finally:
    print( "cleaning up GPIO now." )
    chimes.disable_GPIOs()    
    
    
    
    
    





