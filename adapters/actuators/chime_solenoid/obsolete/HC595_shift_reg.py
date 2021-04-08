import spidev
import time
import RPi.GPIO as GPIO


def gpio_reset( pin_num ):
    GPIO.setup( pin_num, GPIO.OUT)
    GPIO.output( pin_num, GPIO.HIGH)

class HC595():
  def __init__(self, bus=0, deviceId=0, oe_=8, load_clock=25, speed_hz=1000000):  
    self.deviceId = deviceId
    self.bus = bus
    self.oe_ = oe_
    self.load_clock = load_clock
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

    # config output and load_clock
    GPIO.setup( self.oe_, GPIO.OUT )
    GPIO.setup( self.load_clock, GPIO.OUT )

    # keep enabled while running... maybe consider turning it off when values are zero...
    GPIO.output( self.oe_, GPIO.LOW )

    # initial value    
    GPIO.output( self.load_clock, GPIO.LOW )


  def write( self, val ):
    GPIO.output( self.load_clock, GPIO.HIGH )
    self.spiRW( val, self.speed, 20 )  
    time.sleep( 0.000001 )
    GPIO.output( self.load_clock, GPIO.LOW )

  def spiRW(self, values, speed, delay):
    #print("values are: ", values )
    #msg = self.spi.xfer( values, speed, delay )
    self.spi.writebytes( values )
    
  def disable_Output_Enable( self ):
    # enable output
    GPIO.setup( self.oe_, GPIO.OUT )
    GPIO.output( self.oe_, GPIO.HIGH )
    

