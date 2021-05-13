import time
import RPi.GPIO as GPIO


def gpio_reset( pin_num ):
    GPIO.setup( pin_num, GPIO.OUT)
    GPIO.output( pin_num, GPIO.HIGH)

class LJ12A3():
    def __init__( self, oe=12 ):  
        self.oe = oe

        GPIO.setmode(GPIO.BCM)

        # configure output enable on sensor
        GPIO.setup( self.oe, GPIO.OUT )
        GPIO.output( self.oe, GPIO.HIGH )

        # configure inputs from inductive proximity sensors
        #pullDir = GPIO.PUD_UP
        pullDir = GPIO.PUD_DOWN
        GPIO.setup( 27, GPIO.IN, pull_up_down = pullDir )
        GPIO.setup( 22, GPIO.IN, pull_up_down = pullDir )
        GPIO.setup( 23, GPIO.IN, pull_up_down = pullDir )
        GPIO.setup( 24, GPIO.IN, pull_up_down = pullDir )
        GPIO.setup( 25, GPIO.IN, pull_up_down = pullDir )
    
        # keep enabled while running... 

    def read( self ):
        val = [ 0 ] * 5
        val[ 0 ] = GPIO.input( 27 )
        val[ 1 ] = GPIO.input( 22 )
        val[ 2 ] = GPIO.input( 23 )
        val[ 3 ] = GPIO.input( 24 )
        val[ 4 ] = GPIO.input( 25 )
        return val
        

##########################################################

'''
import time

import RPi.GPIO as GPIO


def gpio_reset( pin_num ):
    GPIO.setup( pin_num, GPIO.OUT)
    GPIO.output( pin_num, GPIO.HIGH)

class PM_25():
  def __init__( self, gpio_pin = 8 ):  
    self.gpio_pin = gpio_pin
    GPIO.setmode(GPIO.BCM)
    try:
      pass
    except:
      print("Could not")

    # silly cleanup
    #gpio_reset(  8 )
    #gpio_reset(  7 )
    #gpio_reset( 18 )
    #gpio_reset( 17 )
    #gpio_reset( 16 )
    #gpio_reset(  5 )

    #GPIO.setup( self.gpio_pin, GPIO.IN )
    #GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN )
    GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP )

  def read_it( self ):
    val = GPIO.input( self.gpio_pin )
    return val

'''
