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

spiRW(5, [0x10], 5000, 20)

spiRW(5, [0x00], 5000, 20)

spiRW(5, [0x00], 5000, 20)

spiRW(5, [0x00], 5000, 20)

spiRW(5, [0x00], 5000, 20)

spiRW(5, [0x00], 5000, 20)
