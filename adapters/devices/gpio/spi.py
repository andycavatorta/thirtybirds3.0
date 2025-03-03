"""
Thirtybirds Style Requirements:
    Single and multiple devices
    Synchronous requests for value
    Synchronous requests for change
    Async polling and reporting
    callback for exceptions
    callback for events
    device name can be optionally set or automatically created

    devices do not use thirtybirds
    devices do not use logging
    devices do not use the settings module directly
    devices do not call fault states

    https://pypi.org/project/spidev/
"""
import inspect
import os
import sys
import threading
import time
import traceback

import spidev

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from gpio import binary_output

class SPI():
    def __init__(
        self,
        exception_receiver,
        chip_select_pins_by_name,
        name,
        mode=0b00,
        bus_number=0,
        device_number=0,
        speed_hz=1953125,
        spi_delay=400,
    ):
        ### S C O P E   P A R A M S   T O   S E L F ###
        self.exception_receiver = exception_receiver
        self.chip_select_pins_by_name = chip_select_pins_by_name
        self.name = name

        self.speed_hz = speed_hz
        self.delay_usec = spi_delay  # microseconds

        ### C R E A T E   C H I P   S E L E C T   O U T P U T S ###
        # to do: replace with dict comprehension if result is legible
        self.chip_select_by_name = {}
        for self.name, pin_number in chip_select_pins_by_name.items():
            self.chip_select_by_name[self.name] = binary_output.Output(
                pin_number,
                exception_receiver,
                f"spi_chip_select_{self.name}_{pin_number}"
            )

        ### C R E A T E   S P I   I N T E R F A C E ###
        self.spi_lock = threading.Lock()
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(bus_number, device_number)
            self.spi.mode = mode
            self.spi.max_speed_hz = speed_hz
            self.spi.no_cs = True
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
            return
        self.__release_all_chip_selects()

    def close(self):
        """
        to do: finish docstring
        """
        try:
            self.spi.close()
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

    ######################
    ###  P R I V A T E ###
    ######################

    def __release_all_chip_selects(self):
        for out in self.chip_select_by_name.values():
            out.set_value(True)

    ####################
    ###  P U B L I C ###
    ####################

    def transfer(self, _name_, _list_of_values_):
        response = None
        with self.spi_lock:
            self.chip_select_by_name[_name_].set_value(False)
            #time.sleep(self.delay_usec)
            try:
                response = self.spi.xfer(_list_of_values_, self.delay_usec)
            except Exception as e:
                self.exception_receiver(self.name, e)

                exc_type, exc_value, exc_traceback = sys.exc_info()
                #print(decorator_self.__class__.__name__, function_ref.__name__)
                exception_details = {
                    "script_name":__file__,
                    "class_name":self.__class__.__name__,
                    "method_name":inspect.currentframe().f_code.co_name,
                    "stacktrace":traceback.format_exception(exc_type, exc_value,exc_traceback)
                }

                self.exception_receiver("captured exception", exception_details)
            #time.sleep(self.delay_usec)
            self.chip_select_by_name[_name_].set_value(True)
            return response

    def readbytes(self):
        """
        to do: finish when needed
        """
        pass

    def writebytes(self, _list_of_values_):
        """
        to do: finish when needed
        """
        pass
