import spidev
import time
import RPi.GPIO as GPIO


class AMT203():
  BYTEORDER = "big"
    
  NO_OP = 0x00
  READ_POS = 0x10
  SET_ZERO = 0x70
  ACK_ZERO = 0x80
  WAIT = 0xA5
    
  def __init__(self, 
               bus_number=0, 
               device_number=0, 
               gpios_for_chip_select=[8], 
               speed_hz=1953125,
               delay=40):       # cs=16
    self.speed_hz = speed_hz
    self.gpios_for_chip_select = gpios_for_chip_select
    self.delay_usec = delay     # microseconds
    self.delay_sec = delay / 1E3

    GPIO.setmode(GPIO.BCM)
    self.spi = spidev.SpiDev()
    self.spi.open(bus_number, device_number)
    self.spi_speed = speed_hz
    self.spi.mode = 0b00
    self.spi.no_cs = True 

    for pin in gpios_for_chip_select:
      GPIO.setup(pin, GPIO.OUT)
      GPIO.output(pin, GPIO.HIGH)

  def close(self):
    self.spi.close()

  def from_bytes(self, value: bytes) -> int:
    return int.from_bytes(value, self.BYTEORDER)

  def spi_write_read(self, chip_select_pin, output_bytes) -> bytes:
    GPIO.output(chip_select_pin, GPIO.LOW)
    time.sleep(self.delay_sec)
    received_bytes = self.spi.xfer(output_bytes, self.speed_hz, self.delay_usec)
    GPIO.output(chip_select_pin, GPIO.HIGH)
    return received_bytes

  def spi_clean_buffer(self, chip_select_pin):
    first_result = self.spi_write_read(chip_select_pin, [self.NO_OP])
    while first_result[0] != self.WAIT:
      first_result = self.spi_write_read(chip_select_pin, [self.NO_OP])

  def get_position(self, chip_select_pin) -> int:
    request = self.spi_write_read(chip_select_pin, [self.READ_POS])
    counter = 0
    while request[0] != self.READ_POS:
      request = self.spi_write_read(chip_select_pin, [self.NO_OP])
      counter += 1
      if counter == 100:
          return -1
    position_bytes = self.spi_write_read(chip_select_pin, [self.NO_OP])
    position_bytes += self.spi_write_read(chip_select_pin, [self.NO_OP])
    return self.from_bytes(position_bytes)
  
  def get_presence(self, chip_select_pin) -> bool:
    return self.get_position(chip_select_pin) > -1

  def set_zero(self, chip_select_pin) -> bool:
    """ Must power-cycle to start using new zero point """
    request = self.spi_write_read(chip_select_pin, [self.SET_ZERO])
    counter = 0
    while request[0] != self.ACK_ZERO:
      request = self.spi_write_read(chip_select_pin, [self.NO_OP])
      counter += 1
      if counter == 100:
        return False
    return True

  def get_positions(self) -> list:
    positions = []
    for gpio_for_chip_select in self.gpios_for_chip_select:
      positions.append(self.get_position(gpio_for_chip_select))
    return positions

  def get_presences(self) -> list:
    presences = []
    for gpio_for_chip_select in self.gpios_for_chip_select:
      presences.append(self.get_presence(gpio_for_chip_select))
    return presences
