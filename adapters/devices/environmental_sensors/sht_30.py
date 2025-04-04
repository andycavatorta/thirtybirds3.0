"""
to do: finish docstring
"""

import os
import sys
import threading
import time

import smbus2

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "binary_output"))
)

import output


NAME = __name__

I2C_ADDRESS = 0x44
REQUEST_DATA_COMMAND = 0x2C
USE_HIGH_REPEATABILITY = 0x06
FETCH_DATA_COMMAND = 0x00
RESET_COMMAND = [0x30, 0xA2]


OVER_TEMPERATURE = "OVER_TEMPERATURE"
UNDER_TEMPERATURE = "UNDER_TEMPERATURE"
OVER_HUMIDITY = "OVER_HUMIDITY"
UNDER_HUMIDITY = "UNDER_HUMIDITY"
TEMPERATURE_CHANGE = "TEMPERATURE_CHANGE"
HUMIDITY_CHANGE = "HUMIDITY_CHANGE"


class SHT30(threading.Thread):
    """
    to do: finish docstring
    """

    def __init__(
        self,
        status_receiver,
        exception_receiver,
        maximum_retries_for_bad_read,
        minimum_temp_change_for_callback=0,
        minimum_temp_for_callback=-1,
        maximum_temp_for_callback=-1,
        minimum_humidity_change_for_callback=0,
        minimum_humidity_for_callback=-1,
        maximum_humidity_for_callback=-1,
        optional_power_pin=-1,
        async_data_callback=lambda x: None,
        poll_interval=0,
    ):
        """
        to do: finish docstring
        """
        threading.Thread.__init__(self)
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.maximum_retries_for_bad_read = maximum_retries_for_bad_read
        self.minimum_temp_change_for_callback = minimum_temp_change_for_callback
        self.minimum_temp_for_callback = minimum_temp_for_callback
        self.maximum_temp_for_callback = maximum_temp_for_callback
        self.minimum_humidity_change_for_callback = minimum_humidity_change_for_callback
        self.minimum_humidity_for_callback = minimum_humidity_for_callback
        self.maximum_humidity_for_callback = maximum_humidity_for_callback
        self.optional_power_pin = optional_power_pin
        self.poll_interval = max(poll_interval, 5)
        self.async_data_callback = async_data_callback
        self.initilize()
        time.sleep(1)
        self.last_temperature = -1
        self.last_humidity = -1
        self.last_read_time = time.time()
        self.retries_for_bad_read = 0

        if self.optional_power_pin > -1:
            self.device_power = output.Output(
                status_receiver, exception_receiver, optional_power_pin
            )

        if poll_interval > 0:
            self.start()

    def initilize(self):
        try:
            self.bus = smbus2.SMBus(1)
        except Exception as e:
            self.exception_receiver(NAME, type(e))


    def set_power(self, on_off):
        """
        to do: finish docstring
        """
        if self.optional_power_pin > -1:
            self.device_power.set_value(on_off)

    def get_presence(self):
        """
        to do: finish docstring
        """
        try:
            self.get_temperature()
            return True
        except OSError:
            return False
        return False

    def get_temperature(self):
        """
        to do: finish docstring
        """
        self.set_power(True)
        time.sleep(0.1)
        try:
            self.bus.write_i2c_block_data(
                I2C_ADDRESS, REQUEST_DATA_COMMAND, [USE_HIGH_REPEATABILITY]
            )
            # self.bus.write_byte_data(
            #    I2C_ADDRESS,
            #    REQUEST_DATA_COMMAND,
            #    USE_HIGH_REPEATABILITY
            # )
            time.sleep(0.5)
            data = self.bus.read_i2c_block_data(I2C_ADDRESS, FETCH_DATA_COMMAND, 6)
            time.sleep(0.1)
            self.set_power(False)
            temperature_c = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
            print("temp=",data)
            self.retries_for_bad_read = 0
            return temperature_c
        except OSError:
            #self.retries_for_bad_read += 1
            #self.bus.write_i2c_block_data(I2C_ADDRESS, RESET_COMMAND[0], RESET_COMMAND[1:])
            time.sleep(2)
            self.initilize()
            time.sleep(2)
            print(f"sht_30 bad read {self.retries_for_bad_read} / {self.maximum_retries_for_bad_read}")
            if self.retries_for_bad_read > self.maximum_retries_for_bad_read:
                self.exception_receiver(NAME, type(e))
                return None
        except Exception as e:
            self.exception_receiver(NAME, type(e))

    def get_humidity(self):
        """
        to do: finish docstring
        """
        try:
            self.set_power(True)
            time.sleep(0.1)
            self.bus.write_i2c_block_data(
                I2C_ADDRESS, REQUEST_DATA_COMMAND, [USE_HIGH_REPEATABILITY]
            )
            time.sleep(0.5)
            data = self.bus.read_i2c_block_data(I2C_ADDRESS, FETCH_DATA_COMMAND, 6)
            time.sleep(0.1)
            self.set_power(False)
            humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
            self.retries_for_bad_read = 0
            return humidity
        except OSError:
            #self.retries_for_bad_read += 1
            #self.bus.write_i2c_block_data(I2C_ADDRESS, RESET_COMMAND[0], RESET_COMMAND[1:])
            time.sleep(2)
            self.initilize()
            time.sleep(2)
            # self.bus.write_i2c_block_data(I2C_ADDRESS, RESET_CMD, 0)
            print(f"sht_30 bad read {self.retries_for_bad_read} / {self.maximum_retries_for_bad_read}")
            if self.retries_for_bad_read > self.maximum_retries_for_bad_read:
                self.exception_receiver(NAME, type(e))
                return None
        except Exception as e:
            self.exception_receiver(NAME, type(e))
            return None

    def get_temperature_change(self):
        """
        this sensor is likely to produce noisy measurements
        so this method is most useful when used with
        self.minimum_temp_change_for_callback
        """
        temperature = self.get_temperature()
        temperature_has_changed = False

        delta = self.last_temperature - temperature
        # if there is a threshold
        if self.minimum_temp_change_for_callback > 0:
            if (
                abs(temperature - self.last_temperature)
                > self.minimum_temp_change_for_callback
            ):
                temperature_has_changed = True
                self.last_temperature = temperature
            else:
                temperature_has_changed = False

        # if there is no threshold
        else:
            if temperature != self.last_temperature:
                temperature_has_changed = True
                self.last_temperature = temperature
            else:
                temperature_has_changed = False

        return (temperature_has_changed, temperature, delta)

    def get_humidity_change(self):
        """
        this sensor is likely to produce noisy measurements
        so this method is most useful when used with
        self.minimum_humidity_change_for_callback
        """
        humidity = self.get_humidity()
        humidity_has_changed = False

        delta = self.last_humidity - humidity
        # if there is a threshold
        if self.minimum_humidity_change_for_callback > 0:
            if (
                abs(humidity - self.last_humidity)
                > self.minimum_humidity_change_for_callback
            ):
                humidity_has_changed = True
                self.last_humidity = humidity
            else:
                humidity_has_changed = False

        # if there is no threshold
        else:
            if humidity != self.last_humidity:
                humidity_has_changed = True
                self.last_humidity = humidity
            else:
                humidity_has_changed = False

        return (humidity_has_changed, humidity, delta)

    def get_over_temperature(self):
        """
        to do: finish docstring
        """
        if self.maximum_temp_for_callback == -1:
            return False
        temperature = self.get_temperature()
        if temperature is None:
            print("temperature is None. to do: reset on error")
            return False
        if temperature >= self.maximum_temp_for_callback:
            return True
        return False

    def get_under_temperature(self):
        """
        to do: finish docstring
        """
        if self.minimum_temp_for_callback == -1:
            return False
        if self.get_temperature() >= self.minimum_temp_for_callback:
            return True
        return False

    def get_over_humidity(self):
        """
        to do: finish docstring
        """
        if self.maximum_humidity_for_callback == -1:
            return False
        if self.get_humidity() >= self.maximum_humidity_for_callback:
            return True
        return False

    def get_under_humidity(self):
        """
        to do: finish docstring
        """
        if self.minimum_humidity_for_callback == -1:
            return False
        if self.get_humidity() >= self.minimum_humidity_for_callback:
            return True
        return False

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            time.sleep(self.poll_interval)
            temperature = self.get_temperature()
            humidity = self.get_humidity()
            if self.get_over_temperature():
                self.async_data_callback(OVER_TEMPERATURE, temperature)
            if self.get_under_temperature():
                self.async_data_callback(UNDER_TEMPERATURE, temperature)
            if self.get_over_humidity():
                self.async_data_callback(OVER_HUMIDITY, humidity)
            if self.get_under_humidity():
                self.async_data_callback(UNDER_HUMIDITY, humidity)
            if self.get_temperature_change():
                self.async_data_callback(TEMPERATURE_CHANGE, temperature)
            if self.get_humidity_change():
                self.async_data_callback(HUMIDITY_CHANGE, humidity)


###############
### T E S T ###
###############

class CaptureLocalDetails:
    def __init__(self):
        pass

    def get_location(self, *args):
        pass

class Status_Receiver_Stub:
    capture_local_details = CaptureLocalDetails()

    class Types:
        INITIALIZATIONS = "INITIALIZATIONS"
        TIMEOUT = "TIMEOUT"

    def __init__(self):
        pass

    def collect(self, *args):
        print(args)

def data_callback(current_value):
    print(current_value)

def exception_callback(name, e):
    print(name, e)


def make_sht():
    return SHT30(
            Status_Receiver_Stub(),
            exception_callback,
            async_data_callback = data_callback
    )
"""
        status_receiver,
        minimum_temp_change_for_callback=0,
        minimum_temp_for_callback=-1,
        maximum_temp_for_callback=-1,
        minimum_humidity_change_for_callback=0,
        minimum_humidity_for_callback=-1,
        maximum_humidity_for_callback=-1,
        optional_power_pin=-1,
        async_data_callback=lambda x: None,
        poll_interval=0,
"""
