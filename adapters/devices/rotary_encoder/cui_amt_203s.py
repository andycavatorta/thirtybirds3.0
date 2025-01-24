"""
to do:
    add cumulative position counter
    replace all raw GPIOs with output.Output

format for names_and_chip_select_pins:
{
    "a":13,
    "b":5,
    "c":21
}


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


class Encoder:
    """
    to do: finish docstring
    """

    def __init__(self, name, pin, chip_select_output, initial_value):
        """
        to do: finish docstring
        """
        self.name = name
        self.pin = pin
        self.chip_select_output = chip_select_output
        self.last_value = initial_value

    def get_pin(self):
        """
        to do: finish docstring
        """
        return self.pin

    def get_last_value(self):
        """
        to do: finish docstring
        """
        return self.pin

    def set_new_value(self, new_value):
        """
        to do: finish docstring
        """
        if self.last_value != new_value:
            self.last_value = new_value
            return True
        return False


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
        status_receiver,
        exception_receiver,
        names_and_chip_select_pins,
        async_data_callback=lambda x: None,
        polling_interval=0,
        bus_number=0,
        device_number=0,
        speed_hz=1953125,
        spi_delay=40,
    ):
        # scope arguments to self
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.speed_hz = speed_hz
        self.delay_usec = spi_delay  # microseconds
        self.delay_sec = spi_delay / 1e3

        # init spidev
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(bus_number, device_number)
            self.spi_speed = speed_hz
            self.spi.mode = 0b00
            self.spi.no_cs = True
        except Exception as e:
            self.exception_receiver(NAME, type(e))

        self.encoders = {}
        # initialize pins
        for name in names_and_chip_select_pins:

            chip_select_output = self.outputs[name] = output.Output(
                status_receiver, exception_receiver, names_and_chip_select_pins[name]
            )

            # pin = names_and_chip_select_pins[name]
            # GPIO.setup(pin, GPIO.OUT)
            # GPIO.output(pin, GPIO.HIGH)
            self.encoders[name] = Encoder(
                name, pin, chip_select_output, self.get_position(name)
            )

        if polling_interval > 0:
            self.async_data_callback = async_data_callback
            self.polling_interval = polling_interval
            threading.Thread.__init__(self)
            self.start()

        self.status_receiver.collect(
            "started", self.status_receiver.EventTypes.INITIALIZED
        )

    def close(self):
        """
        to do: finish docstring
        """
        try:
            self.spi.close()
        except Exception as e:
            self.exception_receiver(NAME, type(e))

    def from_bytes(self, value: bytes) -> int:
        """
        to do: finish docstring
        """
        return int.from_bytes(value, self.BYTEORDER)

    def spi_write_read(self, name, output_bytes) -> bytes:
        """
        to do: finish docstring
        """
        self.encoders[name].self.chip_select_output.set_value(False)
        # GPIO.output(chip_select_pin, GPIO.LOW)
        time.sleep(self.delay_sec)

        try:
            received_bytes = self.spi.xfer(output_bytes, self.speed_hz, self.delay_usec)
        except Exception as e:
            self.exception_receiver(NAME, type(e))

        self.encoders[name].self.chip_select_output.set_value(True)
        # GPIO.output(chip_select_pin, GPIO.HIGH)
        return received_bytes

    def spi_clean_buffer(self, name):
        """
        to do: finish docstring
        """
        try:
            first_result = self.spi_write_read(name, [self.NO_OP])
            while first_result[0] != self.WAIT:
                first_result = self.spi_write_read(name, [self.NO_OP])
        except Exception as e:
            self.exception_receiver(NAME, type(e))

    def get_position(self, name) -> int:
        """
        to do: finish docstring
        """
        try:
            request = self.spi_write_read(name, [self.READ_POS])
            counter = 0
            while request[0] != self.READ_POS:
                request = self.spi_write_read(name, [self.NO_OP])
                counter += 1
                if counter == 100:
                    return -1
            position_bytes = self.spi_write_read(name, [self.NO_OP])
            position_bytes += self.spi_write_read(name, [self.NO_OP])
            return self.from_bytes(position_bytes)
        except Exception as e:
            self.exception_receiver(NAME, type(e))
            return None

    def get_presence(self, name) -> bool:
        """
        to do: finish docstring
        """
        return self.get_position(name) > -1

    def set_zero(self, name) -> bool:
        """Must power-cycle to start using new zero point"""
        try:
            request = self.spi_write_read(name, [self.SET_ZERO])
            counter = 0
            while request[0] != self.ACK_ZERO:
                request = self.spi_write_read(name, [self.NO_OP])
                counter += 1
                if counter == 100:
                    return False
            return True
        except Exception as e:
            self.exception_receiver(NAME, type(e))
            return None

    def get_positions(self) -> list:
        """
        to do: finish docstring
        """
        positions = []
        for name in self.encoders:
            positions.append(self.get_position(name))
        return positions

    def get_presences(self) -> list:
        """
        to do: finish docstring
        """
        presences = []
        for name in self.encoders:
            presences.append(self.get_presence(self.encoders[name].get_pin()))
        return presences

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            time.sleep(self.polling_interval)
            for name in self.encoders:
                position = self.get_position(name)

                position_is_new = self.encoders[name].set_new_value(position)

                if position_is_new:
                    self.async_data_callback(name, position)


###############
### T E S T ###
###############

# format for names_and_chip_select_pins {"a":13,"b":5}

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
