"""

asdf

"""

import os
import sys
import threading
import time

import spidev

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "binary_output"))
)

import output

try:
    from RPi import GPIO
except ImportError:
    from Mock import GPIO

GPIO.setmode(GPIO.BCM)

NAME = __name__

class Encoder(threading.Thread):
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
        status_receiver,
        exception_receiver,
        name,
        chip_select_pin,
        positions_per_revolution,
        async_data_callback=lambda x: None,
        polling_interval=0,
        bus_number=0,
        device_number=0,
        speed_hz=500000, # 1953125,
        spi_delay=40,
    ):

        # scope arguments to self
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.positions_per_revolution = positions_per_revolution
        self.speed_hz = speed_hz
        self.delay_usec = spi_delay  # microseconds
        self.delay_sec = spi_delay / 1e3

        self.last_value = -1

        # init spidev
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(bus_number, device_number)
            #self.spi_speed = speed_hz
            self.spi.mode = 0b00
            self.spi.no_cs = True
        except Exception as e:
            self.exception_receiver(NAME, type(e))

        # initialize pins
        self.chip_select_output = output.Output(
            status_receiver, exception_receiver, chip_select_pin
        )

        if polling_interval > 0:
            self.async_data_callback = async_data_callback
            self.polling_interval = polling_interval
            threading.Thread.__init__(self)
            self.start()

        self.status_receiver.collect(
            "started", self.status_receiver.EventTypes.INITIALIZED
        )


    ####################
    ###  P U B L I C ###
    ####################

    def get_presence(self) -> bool:
        """
        to do: finish docstring
        """
        return self.get_position() > -1


    def get_position(self) -> int:
        """
        to do: finish docstring
        """
        try:
            request = self.__spi_write_read([self.READ_POS])
            counter = 0
            while request[0] != self.READ_POS:
                request = self.__spi_write_read([self.NO_OP])
                counter += 1
                if counter == 100:
                    return -1
            position_bytes = self.__spi_write_read([self.NO_OP])
            print("first:",position_bytes)
            position_bytes += self.__spi_write_read([self.NO_OP])
            print("second:",position_bytes)
            self.__spi_clean_buffer()
            return self.__from_bytes(position_bytes)
        except Exception as e:
            self.exception_receiver(NAME, type(e))
            self.__spi_clean_buffer()
            return None

    def get_position_degrees(self):
        return (self.get_position() / self.positions_per_revolution) * 360.0

    def set_zero(self) -> bool:
        """Must power-cycle to start using new zero point"""
        try:
            request = self.__spi_write_read([self.SET_ZERO])
            counter = 0
            while request[0] != self.ACK_ZERO:
                request = self.__spi_write_read([self.NO_OP])
                counter += 1
                if counter == 100:
                    return False
            return True
        except Exception as e:
            self.exception_receiver(NAME, type(e))
            return None

    def set_new_value(self,new_value):
        if self.last_value != new_value:
            self.last_value = new_value
            return True
        return False

    def set_async_data_callback(self, method_ref):
        self.async_data_callback = method_ref

    def close(self):
        """
        to do: finish docstring
        """
        try:
            self.spi.close()
        except Exception as e:
            self.exception_receiver(NAME, type(e))


    ######################
    ###  P R I V A T E ###
    ######################

    def __from_bytes(self, value: bytes) -> int:
        """
        to do: finish docstring
        """
        return int.from_bytes(value, self.BYTEORDER)

    def __spi_write_read(self, output_bytes) -> bytes:
        """
        to do: finish docstring
        """
        self.chip_select_output.set_value(False)
        # GPIO.output(chip_select_pin, GPIO.LOW)
        time.sleep(self.delay_sec)

        try:
            received_bytes = self.spi.xfer(output_bytes, self.speed_hz, self.delay_usec)
        except Exception as e:
            self.exception_receiver(NAME, type(e))

        self.chip_select_output.set_value(True)
        # GPIO.output(chip_select_pin, GPIO.HIGH)
        return received_bytes

    def __spi_clean_buffer(self):
        """
        to do: finish docstring
        """
        try:
            first_result = self.__spi_write_read([self.NO_OP])
            while first_result[0] != self.WAIT:
                first_result = self.__spi_write_read([self.NO_OP])
        except Exception as e:
            self.exception_receiver(NAME, type(e))


    def run(self):
        """
        to do: finish docstring
        """
        while True:
            time.sleep(self.polling_interval)
            position = self.get_position()
            position_is_new = self.set_new_value(position)
            if position_is_new:
                self.async_data_callback(self.name, self.get_position_degrees(), position)


###############
### T E S T ###
###############

# format for names_and_chip_select_pins {"a":13,"b":5}
"""
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

def exception_callback(name, e):
    print(name, e)


def data_callback(name, position):
    print(name, position)

def make_encoder(names_and_chip_select_pins,polling_interval = 0):
    return Encoders(
        Status_Receiver_Stub(),
        exception_callback,
        names_and_chip_select_pins,
        data_callback
    )
"""
