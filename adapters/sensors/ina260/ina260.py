import time
import board
import adafruit_ina260

class INA260():
    def __init__(self):
        try:
            i2c = board.I2C()
            self.ina260 = adafruit_ina260.INA260(i2c)
        except ValueError:
            print("not device found")
            #add feedback through tb?
    def get_current(self):
        return self.ina260.current

    def get_min_max_sample(self, ms=1000):
        end_time = time.time() + (ms/1000.0)
        minimum_current = 0
        maximum_current = 0
        while time.time() < end_time:
            current = self.ina260.current
            if minimum_current > current:
                minimum_current = current
            if maximum_current < current:
                maximum_current = current
        return [minimum_current, maximum_current]

    def get_voltage(self):
        return self.ina260.voltage

    def get_power(self):
        return self.ina260.power
