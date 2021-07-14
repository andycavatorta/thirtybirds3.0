import spidev
import time
import RPi.GPIO as GPIO

pins = [8,7,18,17,16,5]

GPIO.setmode(GPIO.BCM)
spi = spidev.SpiDev()
bus = 0
device = 0
spi.open(bus, device)

# Settings (for example)
spi_speed = 1000000
spi.mode = 0b00
spi.no_cs = True

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  

while True:
    for pin in pins:
        #GPIO.output(pin, GPIO.LOW)
        #msg = spi.xfer(values, speed, delay)
        #GPIO.output(pin, GPIO.HIGH)

        attempts = 0
        first_result = spiRW([0x10],spi_speed,20)  

        while True:
          first_result = spiRW([0x00],spi_speed,20)
          attempts = attempts + 1
          if attempts > 100: 
            print(" yuk")
          
          if first_result[ 0 ] != 0x10:
            break;

        attempts = 0
        while True:
          tmp = spi( [0x00], spi_speed, 20 )
          if tmp[ 0 ] == 0x10:
            msb_result = spi( [0x00], spi_speed, 20 )
            break;
          attempts = attempts + 1
          if attempts > 100: 
            print(" yuk2 ")
            pass

        lsb_result = spiRW([0x00],spi_speed,20)
        final_result = (msb_result[0]<<8 | lsb_result[0])
        while True:
            first_result = spiRW([0x00],spi_speed,20)
            if first_result[ 0 ] == 165:
                break;

        print("final_result",final_result)

def clean_buffer():
    while True:
        first_result = spiRW([0x00],spi_speed,20)
        if first_result[ 0 ] == 165:
            break;

def spiRW(cs, values, speed, delay):
    GPIO.output(cs, GPIO.LOW)
    #time.sleep(.01)
    msg = spi.xfer(values, speed, delay)
    GPIO.output(cs, GPIO.HIGH)
    return msg
