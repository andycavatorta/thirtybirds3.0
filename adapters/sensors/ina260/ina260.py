import time
import board
import adafruit_ina260

class INA260():
    def __init__(self,callback):
        self.callback = callback
        try:
            i2c = board.I2C()
            self.ina260 = adafruit_ina260.INA260(i2c)
            self.present = True
        except ValueError:
            self.present = False

    def get_present(self):
        return self.present

    def get_voltage(self):
        try:
            return self.ina260.voltage
        except Exception:
            self.callback("present",False)
            return None

    def get_power(self):
        try:
            return self.ina260.power
        except Exception:
            self.callback("present",False)
            return None

    def get_current(self):
        try:
            return self.ina260.current
        except Exception:
            self.callback("present",False)
            return None

    def get_min_max_sample(self, ms=1000):
        try:
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
        except Exception:
            self.callback("present",False)
            return None
