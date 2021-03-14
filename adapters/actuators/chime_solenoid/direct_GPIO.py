import spidev
import time
import RPi.GPIO as GPIO


class gpio_based():
  def __init__(self, deviceId=0, chimeGPIOs )
    self.deviceId = deviceId
    self.chimeGPIOs = chimeGPIOs

    GPIO.setmode(GPIO.BCM)

    # config and turn off
    for gpio in self.chimeGPIOS:
      GPIO.setup( gpio, GPIO.OUT )
      GPIO.output( gpio GPIO.LOW )


  # send a vector of 5 ints, no bit packing etc. to GPIOs
  def write( self, chime_vec ):
    for gpio in range( 0, 5 ):

      outval = GPIO.LOW
      if chime_vec[ cou ] != 0:
        outval = GPIO.HIGH
      GPIO.output( gpio, outval )

    #print("values are: ", chime_vec )
    
  # disable GPIOs driving
  def disable_GPIOs( self ):
    for gpio in self.chimeGPIOS:
      GPIO.setup( gpio, GPIO.IN )
      GPIO.output( gpio, GPIO.HIGH )
    

