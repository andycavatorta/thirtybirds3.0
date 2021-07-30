import time
import board
import adafruit_ina260

class INA260():
    def __init__(self):
        i2c = board.I2C()
        self.ina260 = adafruit_ina260.INA260(i2c)

    def get_current(self):
        return self.ina260.current

    def get_voltage(self):
        return self.ina260.current

    def get_power(self):
        return self.ina260.power
