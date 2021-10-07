import spidev
import time
import RPi.GPIO as GPIO

pins = [13,12,18,17,16,5]

GPIO.setmode(GPIO.BCM)
spi = spidev.SpiDev()
bus = 0
device = 0
spi.open(bus, device)

# Settings (for example)
spi_speed = 5000
spi.mode = 0b00
spi.no_cs = True

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  

def clean_buffer():
    while True:
        first_result = spiRW(pin,[0x00],spi_speed,20)
        if first_result[ 0 ] == 165:
            break;

def spiRW(cs, values, speed, delay):
    GPIO.output(cs, GPIO.LOW)
    time.sleep(.01)
    msg = spi.xfer(values, speed, delay)
    GPIO.output(cs, GPIO.HIGH)
    return msg

def get_position(cs):
    first_result = spiRW([0x10],0,20)
    while first_result[0] != 16:
      first_result = spiRW([0x00],0,20)
    request = spiRW(cs, [0x10], 5000, 20)
    blank_byte_165 = spiRW(cs, [0x00], 5000, 20)
    blank_byte_16 = spiRW(cs, [0x00], 5000, 20)
    most_significant_byte = spiRW(cs, [0x00], 5000, 20)
    least_significant_byte = spiRW(cs, [0x00], 5000, 20)
    clean_buffer()
    return (most_significant_byte[0]<<8 | least_significant_byte[0])


"""
def get_position(cs):
    print(spiRW(cs, [0x10], 5000, 20))
    print(spiRW(cs, [0x00], 5000, 20))
    print(spiRW(cs, [0x00], 5000, 20))
    print(spiRW(cs, [0x00], 5000, 20))
    print(spiRW(cs, [0x00], 5000, 20))
    print(spiRW(cs, [0x00], 5000, 20))

spiRW(cs, [0x70], 5000, 20)
"""

def set_zero(self):
    self.clean_buffer()
    first_result = self.spiRW([0x70],self.speed,20)
    while first_result[0] != 128:
      first_result = self.spiRW([0x00],self.speed,20)
    print("Zero set was successful and the new position offset is stored in EEPROM")
    self.clean_buffer()
    time.sleep(0.1)




def get_positions():
    for pin in pins:
        time.sleep(0.01)
        print(pin, get_position(pin))       
