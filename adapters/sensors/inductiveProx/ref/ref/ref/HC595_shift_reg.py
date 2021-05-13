import spidev
import time
import RPi.GPIO as GPIO


def gpio_reset( pin_num ):
    GPIO.setup( pin_num, GPIO.OUT)
    GPIO.output( pin_num, GPIO.HIGH)

class HC595():
  def __init__(self, bus=0, deviceId=0, cs=25, speed_hz=1000000):  
    self.deviceId = deviceId
    self.bus = bus
    self.cs = cs
    self.speed = speed_hz
    GPIO.setmode(GPIO.BCM)
    try:
      print("bus: %s | pin: %s" % (self.bus, self.deviceId))
      self.spi = spidev.SpiDev()
      self.spi.open(self.bus, self.deviceId)
      self.open = True
      self.spi.mode = 0b00
      self.spi.no_cs = True
      self.spi.max_speed_hz = speed_hz
      print("SPI connected. Device id: ", self.deviceId)
    except:
      self.open = False
      print("Could not connect to SPI device")

    # silly cleanup
    #gpio_reset(  8 )
    #gpio_reset(  7 )
    #gpio_reset( 18 )
    #gpio_reset( 17 )
    #gpio_reset( 16 )
    #gpio_reset(  5 )

    GPIO.setup(self.cs, GPIO.OUT)
    GPIO.output(self.cs, GPIO.LOW)


  def write( self, val ):
    self.spiRW( val, self.speed, 20 )  
    GPIO.output(self.cs, GPIO.HIGH)
    time.sleep( 0.000001 )
    GPIO.output(self.cs, GPIO.LOW)

  def spiRW(self, values, speed, delay):
    #print("values are: ", values )
    #msg = self.spi.xfer( values, speed, delay )
    self.spi.writebytes( values )

