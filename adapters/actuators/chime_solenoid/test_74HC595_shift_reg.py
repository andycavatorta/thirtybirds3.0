#!/usr/bin/env python

import time

import HC595_shift_reg as shifter

reg = shifter.HC595()

seq = [ 1, 0, 0, 1, 1, 0, 0, 0 ]

#seq = [ 1, 0, 0, 0, 1, 0, 0, 0,  1, 0, 1, 0, 1, 0, 1, 0,  1, 0, 0, 1, 0, 0, 1, 0,   1, 0, 0, 1, 0, 0, 1, 1 ]
seq_step = 0

val = [ 0 ]
while True:

    if seq[ seq_step ] == 1:    
        val[ 0 ] = 0xff
    else:
        val[ 0 ] = 0x00
    print( val )
    reg.write( val )
    time.sleep( .010 )

    val[ 0 ] = 0x00
    print( val )
    reg.write( val )
    time.sleep( 0.165 )

    seq_step = seq_step + 1
    if seq_step >= 8:
        seq_step = 0
    
    





