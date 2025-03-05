"""

asdf

"""

import inspect
import traceback
import os
import sys
import threading
import time

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from gpio import spi

import event_names
import unit_names

class Encoders(threading.Thread):
    """
    to do: finish docstring
    """

    BYTEORDER = "big"
    NO_OP = 0x00
    READ_POS = 0x10
    SET_ZERO = 0x70
    ACK_ZERO = 0x80
    WAIT = 0xA5

    def __init__(
        self,
        exception_receiver,
        event_receiver,
        name,
        chip_select_pins_by_name,
        positions_per_revolution,
        polling_interval=0,
    ):
        threading.Thread.__init__(self)

        ### S C O P E   P A R A M S   T O   S E L F ###
        self.exception_receiver = exception_receiver
        self.event_receiver = event_receiver
        self.name = name
        self.chip_select_pins_by_name = chip_select_pins_by_name
        self.positions_per_revolution = positions_per_revolution
        self.encoders = {}

        ### C R E A T E   D E V I C E S ###
        self.spi_connections = spi.SPI(
            exception_receiver,
            chip_select_pins_by_name,
            f"{name}_spi_interface",
        )

        self.encoder_values = {}
        for key in self.chip_select_pins_by_name.keys():
            self.encoders[key] = None

        ### T H R E A D   S T U F F  ###
        if polling_interval > 0:
            self.polling_interval = polling_interval
            self.start()

        self.rotary_unit_converter = unit_names.Rotary_Unit_Converter(self.positions_per_revolution)
        self.rotary_distance_to_orientation_converter = unit_names.Rotary_Distance_To_Orientation_Converter(self.positions_per_revolution)

    ####################
    ###  P U B L I C ###
    ####################

    def get_presence(self, _name_ = None):
        """
        ---
        """
        self.spi_connections.transfer(_name_, [self.READ_POS])
        counter = 0
        response = self.spi_connections.transfer(_name_, [self.NO_OP])
        while response[0] != self.READ_POS:
            response = self.spi_connections.transfer(_name_, [self.NO_OP])
            counter += 1
            if counter == 100:
                return False
        self.spi_connections.transfer(_name_, [self.NO_OP])
        self.spi_connections.transfer(_name_, [self.NO_OP])
        return True

    def get_position(self, _name_ = None, unit=unit_names.PULSES):
        """
        ---
        """
        response = self.spi_connections.transfer(_name_, [self.READ_POS])
        counter = 0
        #response = self.spi_connections.transfer(_name_, [self.NO_OP])
        while response[0] != self.READ_POS:
            response = self.spi_connections.transfer(_name_, [self.NO_OP])
            counter += 1
            if counter == 100:
                self.event_receiver(
                    self.name,
                    event_names.COMMUNICATION_FAILED,
                    None
                )
                # call error in event_receiver
                return None
        position_bytes = self.spi_connections.transfer(_name_, [self.NO_OP])
        position_bytes += self.spi_connections.transfer(_name_, [self.NO_OP])
        position_int = int.from_bytes(position_bytes, self.BYTEORDER)
        return self.rotary_unit_converter.convert(position_int, unit_names.PULSES, unit)

    def set_zero(self, _name_ = None):
        """Must power-cycle to start using new zero point"""
        try:
            request = self.spi_connections.transfer(_name_, [self.SET_ZERO])
            counter = 0
            while request[0] != self.ACK_ZERO:
                request = self.spi_connections.transfer(_name_, [self.NO_OP])
                counter += 1
                if counter == 100:
                    return False
            return True
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
            return None

    def run(self):
        while True:
            time.sleep(self.polling_interval)
            for _name_ in self.chip_select_pins_by_name.keys():
                position = self.get_position(_name_)
                if self.encoders[_name_] != position:
                    self.event_receiver(
                        self.name,
                        event_names.CHANGE,
                        (_name_, position)
                    )
                    self.encoders[_name_] = position
