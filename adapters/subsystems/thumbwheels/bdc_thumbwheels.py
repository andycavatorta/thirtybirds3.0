"""
to do: finish docstring
"""

import os
import sys

devices_path = os.path.abspath(
        os.path.join(
            os.path.dirname(
                __file__
            ),
        '..',
        '..',
        'devices',
        'binary_input',
        )
    )
sys.path.append(devices_path)
import binary_inputs

class Thumbwheels:
    """
    The variable gpios_2l is a nested .
    There is one outer cycle for each thumbwheel.
    These represent decimal digits starting " = " the 1s place.
    The inner cycle of each represents the gpios for BDC binary digits 0001 through 1000
    The gpios_2l for 4-digit decimal thumbwheel might look like
    [
        [
            4, #bdc binary one
            3, #bdc binary two
            2, #bdc binary fou
            1 #bdc binary eight
        ], # decimal ones
        [8,7,6,5], # decimal tens
        [11,12,15,13], # decimal hundreds
        [21,22,23,9], # decimal thousands
    ]
    """

    def __init__(
        self,
        status_receiver,
        gpios_2l,  # 2-dimensional list
        data_callback,
        poll_interval=1,
    ):
        """
        to do: finish docstring
        """

        self.gpios_2l = gpios_2l
        self.data_callback = data_callback
        self.status_receiver = status_receiver
        self.poll_interval = poll_interval

        self.decimal_place_values = [0 for i in range(len(self.gpios_2l))]

        self.thumbwheels = []
        for place_name_ordinal, binary_gpios in enumerate(gpios_2l):
            self.thumbwheels.append(
                Thumbwheel(
                    place_name_ordinal,
                    binary_gpios,
                    self.tw_callback,
                    status_receiver,
                    poll_interval,
                )
            )

    def get_value(self):
        return self.calculate_total()

    def calculate_total(self):
        return sum(
            self.decimal_place_values[i] * (10**i)
            for i in range(len(self.decimal_place_values))
        )

    def tw_callback(self, place_name_ordinal, value):
        """
        to do: finish docstring
        """
        self.decimal_place_values[place_name_ordinal] = value
        self.data_callback(self.calculate_total())


class Thumbwheel:
    def __init__(
        self, place_name_ordinal, gpios, data_callback, status_receiver, poll_interval=1
    ):
        """
        to do: finish docstring
        """
        self.place_name_ordinal = place_name_ordinal
        self.gpios = gpios
        self.data_callback = data_callback
        self.status_receiver = status_receiver
        self.poll_interval = poll_interval
        self.binary_value = 0b0000
        self.inputs = binary_inputs.Inputs(
            {
                "one": {
                    "gpio": self.gpios[0],
                    "pull_up_down": -1,
                },
                "two": {
                    "gpio": self.gpios[1],
                    "pull_up_down": -1,
                },
                "four": {
                    "gpio": self.gpios[2],
                    "pull_up_down": -1,
                },
                "eight": {
                    "gpio": self.gpios[3],
                    "pull_up_down": -1,
                },
            },
            self.inputs_callback,
            self.status_receiver,
            self.poll_interval,
        )
        self.status_receiver.collect(
            self.status_receiver.capture_local_details.get_location(self),
            "started",
            self.status_receiver.types.INITIALIZATIONS,
        )

    def inputs_callback(self, gpio_name, gpio_value):
        """
        to do: finish docstring
        """
        place_name_map = {
            "one": 0,
            "two": 1,
            "four": 2,
            "eight": 3,
        }
        if int(gpio_value) == 1:
            self.binary_value |= 1 << place_name_map[gpio_name]
        else:
            self.binary_value &= ~(1 << place_name_map[gpio_name])
        self.data_callback(self.place_name_ordinal, self.binary_value)


###############
### T E S T ###
###############
"""
def data_callback(name, position):
    print(name, position)

class Status_Receiver_Stub:
    class types:
        INITIALIZATIONS = "INITIALIZATIONS"

    def __init__(self):
        pass

    def collect(self, *args):
        pass

thumbwheels = None
def test(gpios_2l):
    global thumbwheels
    thumbwheels =  Thumbwheels(
            gpios_2l, 
            data_callback,
            Status_Receiver_Stub(),
        )
"""
