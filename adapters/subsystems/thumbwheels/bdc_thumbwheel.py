"""
format for gpios
[3,8,2,21]
"""

import os
import sys

devices_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "devices",
        "binary_input",
    )
)
sys.path.append(devices_path)
import binary_inputs


class Thumbwheel:
    """
    to do: finish docstring
    """
    def __init__(self, gpios, data_callback, status_receiver, poll_interval=1):
        """
        to do: finish docstring
        """
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
        self.data_callback(int(self.binary_value))


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

thumbwheel = None
def test(channel_quantity,optional_channel_names):
    global thumbwheel
    thumbwheel =  Thumbwheel(
            gpios,
            data_callback,
            Status_Receiver_Stub(),
        )
"""
