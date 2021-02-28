import spidev
import time
import RPi.GPIO as GPIO

class AMT203():
  def __init__(self, bus=0, deviceId=0, cs=16):
    self.deviceId = deviceId
    self.bus = bus
    self.cs = cs
    GPIO.setmode(GPIO.BCM)
    try:
      print("bus: %s | pin: %s" % (self.bus, self.deviceId))
      self.spi = spidev.SpiDev()
      self.spi.open(self.bus, self.deviceId)
      self.open = True
      print("SPI connected. Device id: ", self.deviceId)
    except:
      self.open = False
      print("Could not connect to SPI device")

    GPIO.setup(self.cs, GPIO.OUT)
    GPIO.output(self.cs, GPIO.HIGH)

  def clean_buffer(self):
    first_result = self.spiRW([0x00],0,20)
    while first_result[0] != 165:
      first_result = self.spiRW([0x00],0,20)

  def get_position(self):
    print(">>> 1")
    first_result = self.spiRW([0x10],0,20)
    print(">>> 2")
    while first_result[0] != 16:
      print(">>> 3")
      first_result = self.spiRW([0x00],0,20)
    print(">>> 4")
    msb_result = self.spiRW([0x00],0,20)
    print(">>> 5")
    lsb_result = self.spiRW([0x00],0,20)
    print(">>> 6")
    # msb_bin = bin(msb_result[0]<<8)[2:]
    # lsb_bin = bin(lsb_result[0])[2:]
    final_result = (msb_result[0]<<8 | lsb_result[0])
    print(">>> 7")
    self.clean_buffer()
    print(">>> 8")
    return final_result

  def set_zero(self):
    self.clean_buffer()
    first_result = self.spiRW([0x70],0,20)
    while first_result[0] != 128:
      first_result = self.spiRW([0x00],0,20)
    print("Zero set was successful and the new position offset is stored in EEPROM")
    self.clean_buffer()
    time.sleep(0.1)

  def get_resolution(self):
    return 4096

  def spiRW(self, values, speed, delay):
    GPIO.output(self.cs, GPIO.LOW)
    msg = self.spi.xfer(values, speed, delay)
    GPIO.output(self.cs, GPIO.HIGH)
    return msg
