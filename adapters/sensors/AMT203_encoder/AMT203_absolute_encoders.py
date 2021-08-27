import spidev
import time
import RPi.GPIO as GPIO

class AMT203():
  def __init__(self, bus_number=0, device_number=0, gpios_for_chip_select=[8], speed_hz=5000):   # cs=16
    self.speed_hz = speed_hz
    self.gpios_for_chip_select = gpios_for_chip_select

    GPIO.setmode(GPIO.BCM)
    self.spi = spidev.SpiDev()
    self.spi.open(bus_number, device_number)
    self.spi_speed = 5000
    self.spi.mode = 0b00
    self.spi.no_cs = True

    for pin in gpios_for_chip_select:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  

  def spi_write_read(self, chip_select_pin, output_byte):
    GPIO.output(chip_select_pin, GPIO.LOW)
    time.sleep(.01)
    received_byte = spi.xfer(output_byte, self.speed_hz, 20)
    GPIO.output(chip_select_pin, GPIO.HIGH)
    return received_byte

  def get_position(self, chip_select_pin):
    request = self.spi_write_read(chip_select_pin, [0x10], 5000, 20)
    blank_byte_165 = self.spi_write_read(chip_select_pin, [0x00], 5000, 20)
    blank_byte_16 = self.spi_write_read(chip_select_pin, [0x00], 5000, 20)
    most_significant_byte = self.spi_write_read(chip_select_pin, [0x00], 5000, 20)
    least_significant_byte = self.spi_write_read(chip_select_pin, [0x00], 5000, 20)
    return (most_significant_byte[0]<<8 | least_significant_byte[0])

  def get_positions(self):
    positions = []
    for gpio_for_chip_select in  self.gpios_for_chip_select:
      positions.append(self.get_position(gpio_for_chip_select))
    return positions


