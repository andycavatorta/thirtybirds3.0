"""
to do: finish docstring
"""

import inspect
import os
import sys
import threading
import time
import traceback

import smbus2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from gpio import binary_output
import event_names

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
        exception_receiver,
        event_receiver,
        maximum_retries_for_bad_read,
        name,
        optional_power_pin=-1,
        poll_interval=0,
        nominal_temp_range=[None, None],
        nominal_humidity_range=[None, None],
        minimum_temp_change_for_report=-1,  # -1 means no report, 0 means report every read, >0 means report only increments
        minimum_humidity_change_for_report=-1,  # -1 means no report, 0 means report every read, >0 means report only increments
    ):
        """
        to do: finish docstring
        """
        threading.Thread.__init__(self)

        ### S E L F   V A R S ###
        self.exception_receiver = exception_receiver
        self.event_receiver = event_receiver
        self.maximum_retries_for_bad_read = maximum_retries_for_bad_read
        self.deveice_name = name
        self.optional_power_pin = optional_power_pin
        self.poll_interval = poll_interval
        self.nominal_temp_range = nominal_temp_range
        self.nominal_humidity_range = nominal_humidity_range
        self.minimum_temp_change_for_report = minimum_temp_change_for_report
        self.minimum_humidity_change_for_report = minimum_humidity_change_for_report
        self.power_output = None
        self.bus = None

        self.last_reported_temp = 0
        self.last_reported_humidity = 0
        self.fault_flag = False

        ### T H R E A D   S T U F F  ###
        self.request_lock = threading.Lock()
        self.fault_flag_lock = threading.Lock()
        if poll_interval > 0:
            self.start()

    #####################
    ### P R I V A T E ###
    #####################

    def init(self):
        if self.optional_power_pin > -1:
            self.power_output = binary_output(
                self.optional_power_pin,
                self.exception_receiver,
                device_name=f"{self.deveice_name}_output_{self.optional_power_pin}",
            )
            self.__cycle_power()

        try:
            self.bus = smbus2.SMBus(1)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            #print(decorator_self.__class__.__name__, function_ref.__name__)
            exception_details = {
                "script_name":__file__,
                "class_name":self.__class__.__name__,
                "method_name":inspect.currentframe().f_code.co_name,
                "stacktrace":traceback.format_exception(exc_type, exc_value,exc_traceback)
            }
            self.exception_receiver(__file__, exception_details)

    def __cycle_power(self):
        if self.optional_power_pin > -1:
            self.power_output.set_value(False)
            time.sleep(2)
            self.power_output.set_value(True)
            time.sleep(2)

    ###################
    ### P U B L I C ###
    ###################

    def get_measurements(self):
        """
        to do: finish docstring
        """
        with self.request_lock:
            for retry in range(self.maximum_retries_for_bad_read):
                try:
                    self.bus.write_i2c_block_data(
                        I2C_ADDRESS, REQUEST_DATA_COMMAND, [USE_HIGH_REPEATABILITY]
                    )
                    time.sleep(0.5)
                    data = self.bus.read_i2c_block_data(
                        I2C_ADDRESS, FETCH_DATA_COMMAND, 6
                    )
                    time.sleep(0.1)
                    temperature_c = (
                        (((data[0] * 256.0) + data[1]) * 175) / 65535.0
                    ) - 45
                    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
                    return (temperature_c, humidity)
                except OSError:
                    self.event_receiver(
                        self.deveice_name, event_names.COMMUNICATION_ERROR, retry
                    )
                    self.__cycle_power()
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    #print(decorator_self.__class__.__name__, function_ref.__name__)
                    exception_details = {
                        "script_name":__file__,
                        "class_name":self.__class__.__name__,
                        "method_name":inspect.currentframe().f_code.co_name,
                        "stacktrace":traceback.format_exception(exc_type, exc_value,exc_traceback)
                    }
                    self.exception_receiver(__file__, exception_details)
            self.event_receiver(self.deveice_name, event_names.COMMUNICATION_FAILED, retry)
            return None

    def get_presence(self):
        response = self.get_measurements()
        return not response is None

    def get_temperature(self):
        response = self.get_measurements()
        if response is None:
            return None
        return None if response is None else response[0]

    def get_humidity(self):
        response = self.get_measurements()
        if response is None:
            return None
        return None if response is None else response[1]

    def set_fault_state(self):
        if self.poll_interval > 0:
            with self.fault_flag_lock:
                self.fault_flag = True

    def report_thresholds_passed(self):
        """
        This is the function that will be polled by the run loop.
        It handles all communication internally and returns nothing
        It can also be called publicly.
        """
        response = self.get_measurements()
        if response is None:
            # error messages have already been sent upstream
            return
        temperature_c, humidity = response
        if self.nominal_temp_range[0] is not None:
            if temperature_c < self.nominal_temp_range[0]:
                self.event_receiver(
                    self.deveice_name,
                    event_names.MIN_THRESHOLD_EXCEEDED,
                    ("temperature", temperature_c),
                )
        if self.nominal_temp_range[1] is not None:
            if temperature_c > self.nominal_temp_range[1]:
                self.event_receiver(
                    self.deveice_name,
                    event_names.MAX_THRESHOLD_EXCEEDED,
                    ("temperature", temperature_c),
                )

        if self.nominal_humidity_range[0] is not None:
            if humidity < self.nominal_humidity_range[0]:
                self.event_receiver(
                    self.deveice_name,
                    event_names.MIN_THRESHOLD_EXCEEDED,
                    ("humidity", humidity),
                )
        if self.nominal_humidity_range[1] is not None:
            if humidity > self.nominal_humidity_range[1]:
                self.event_receiver(
                    self.deveice_name,
                    event_names.MAX_THRESHOLD_EXCEEDED,
                    ("humidity", humidity),
                )

        if self.minimum_temp_change_for_report == 0:
            if self.last_reported_temp != temperature_c:
                self.event_receiver(
                    self.deveice_name, event_names.CHANGE, ("temperature", temperature_c)
                )
            self.last_reported_temp = temperature_c

        if self.minimum_humidity_change_for_report == 0:
            if self.last_reported_humidity != humidity:
                self.event_receiver(
                    self.deveice_name, event_names.CHANGE, ("humidity", humidity)
                )
            self.last_reported_humidity = humidity

        if self.minimum_temp_change_for_report > 0:
            if (
                abs(self.last_reported_temp - temperature_c)
                > self.minimum_temp_change_for_report
            ):
                self.event_receiver(
                    self.deveice_name, event_names.CHANGE, ("temperature", temperature_c)
                )
            self.last_reported_temp = temperature_c

        if self.minimum_humidity_change_for_report == 0:
            if (
                abs(self.last_reported_humidity - humidity)
                > self.minimum_humidity_change_for_report
            ):
                self.event_receiver(
                    self.deveice_name, event_names.CHANGE, ("humidity", humidity)
                )
            self.last_reported_humidity = humidity

    def run(self):
        while True:
            time.sleep(self.poll_interval)
            with self.fault_flag_lock:
                if self.fault_flag:
                    return
            self.report_thresholds_passed()
