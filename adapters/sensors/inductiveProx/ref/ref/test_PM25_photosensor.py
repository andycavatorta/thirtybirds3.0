#!/usr/bin/env python

import time

import LJ12A3 as inductiveProximitySensor

indProx = inductiveProximitySensor.LJ12A3()

while True:

    val = photosensor.read_it()
    print( val )
    time.sleep( 0.0205 )





