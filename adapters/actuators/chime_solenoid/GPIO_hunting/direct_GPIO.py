import time
import RPi.GPIO as GPIO


class gpio_based():
  def __init__(self, chimeGPIOs, deviceId=0 ):
    self.deviceId = deviceId
    self.chimeGPIOs = chimeGPIOs

    GPIO.setmode(GPIO.BCM)

    # config and turn off
    for gpio in self.chimeGPIOs:
      GPIO.setup( gpio, GPIO.OUT )
      GPIO.output( gpio, GPIO.LOW )


  # send a vector of 5 ints, no bit packing etc. to GPIOs
  def write( self, chime_vec ):
    #print("values are: ", chime_vec )
    for idx in range( 0, 5 ):
      outval = GPIO.LOW
      if chime_vec[ idx ] != 0:
        outval = GPIO.HIGH
      gpio = self.chimeGPIOs[ idx ]
      GPIO.output( gpio, outval )
    
  # disable GPIOs driving
  def disable_GPIOs( self ):
    for gpio in self.chimeGPIOs:
      GPIO.output( gpio, GPIO.LOW )
      GPIO.setup( gpio, GPIO.IN )
    

