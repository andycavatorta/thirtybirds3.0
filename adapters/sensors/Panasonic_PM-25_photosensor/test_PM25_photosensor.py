#!/usr/bin/env python

import time

import PM25_photosensor as PM_25

photosensor = PM_25.PM_25()

while True:

    val = photosensor.read_it()
    print( val )
    time.sleep( 0.0205 )





