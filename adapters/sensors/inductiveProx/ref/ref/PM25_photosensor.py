
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

