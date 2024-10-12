#!/usr/bin/env python

import time

import AMT203_absolute_encoder as encoder

amt = encoder.AMT203()


amt.clean_buffer()

while True:
    pos = amt.get_position()
    print( pos )
    time.sleep( .1 )
    





