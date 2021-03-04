#!/usr/bin/env python

import time

import HC595_shift_reg as shifter

reg = shifter.HC595()



seq = [ [ 1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 1, 0 ],
        [ 0, 0, 1, 0,  0, 0, 1, 0,  0, 0, 1, 0,  0, 0, 1, 0 ],
        [ 0, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 0, 0 ],
        [ 0, 1, 0, 1,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 1, 1 ] ]
        
#seq = [ [ 1, 0, 0, 0,  0, 0, 0, 0  ],
#        [ 0, 1, 0, 0,  0, 0, 0, 0  ],
#        [ 0, 0, 1, 0,  0, 0, 0, 0  ],
#        [ 0, 0, 0, 1,  0, 0, 0, 0  ],
#        [ 0, 0, 0, 0,  1, 0, 0, 0  ] ]

#seq = [ 1, 0, 0, 0, 1, 0, 0, 0,  1, 0, 1, 0, 1, 0, 1, 0,  1, 0, 0, 1, 0, 0, 1, 0,   1, 0, 0, 1, 0, 0, 1, 1 ]
seq_step = 0

val = [ 0 ]
while True:

    val[ 0 ] = 0;
    
    for trk in range( 0, 5 ):
    
        if seq[ trk ][ seq_step ] == 1:    
            val[ 0 ] = val[ 0 ] + ( 1 << trk )
            #val[ 0 ] = val[ 0 ] | 0xff
            
    print( val )
    reg.write( val )
    time.sleep( .010 )

    val[ 0 ] = 0x00
    print( val )
    reg.write( val )
    time.sleep( 0.205 )

    seq_step = seq_step + 1
    if seq_step >= 16:
        seq_step = 0
    
    





