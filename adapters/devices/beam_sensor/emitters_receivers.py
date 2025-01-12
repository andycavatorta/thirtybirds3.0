"""
---------------------------
this module must use binary_input rather than binary_inputs and have its own polling thread
because of the need to coordinate the outputs

emitter_receiver_data:{
    "name a":{
        "receiver_pin": 2,
        "pull_up_down": -1,
    },
    "name b":{
        "receiver_pin": 4,
        "emitter_power_pin", 8
    },
    "name c":{
        "receiver_pin": 6,
        "pull_up_down": -1,
    },
    "name d":{
        "receiver_pin": 10,
        "pull_up_down": 1,
        "emitter_power_pin", 13
    },

}

"""

import os
import sys
import time
import threading

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "binary_input"))
)
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "binary_output"))
)

import binary_input
import output


class EmitterReceiver:
    """
    to do: finish docstring
    """

    def __init__(
        self,
        status_receiver,
        receiver_pin,
        pull_up_down=0,
        emitter_power_pin=-1,
    ):
        """
        to do: finish docstring
        """
        self.binary_input = binary_input.Input(
            status_receiver, receiver_pin, pull_up_down
        )
        self.control_emitter_power = emitter_power_pin > -1
        if self.control_emitter_power:
            self.emitter_power = output.Output(status_receiver, emitter_power_pin)
        else:
            self.emitter_power = None

    def __set_emitter_power(self, power_bool):
        """
        to do: finish docstring
        """
        if self.control_emitter_power:
            self.emitter_power.set_value(power_bool)

    def get_change(self):
        """
        to do: finish docstring
        """
        self.__set_emitter_power(True)
        time.sleep(0.05)
        change, value = self.binary_input.get_change()
        self.__set_emitter_power(False)
        return (change, value)


class EmittersReceivers(threading.Thread):
    """
    to do: finish docstring
    """

    def __init__(
        self,
        status_receiver,
        emitter_receiver_data,
        poll_interval,
        async_data_callback,
    ):
        """
        to do: finish docstring
        """
        self.status_receiver = status_receiver
        self.emitter_receiver_data = emitter_receiver_data
        self.poll_interval = poll_interval
        self.async_data_callback = async_data_callback

        self.emitters_receivers = {}
        for emitter_receiver_name in emitter_receiver_data:
            emitter_power_pin = (
                self.emitter_receiver_data[emitter_receiver_name]["emitter_power_pin"]
                if "emitter_power_pin" in self.emitter_receiver_data[emitter_receiver_name]
                else -1
            )
            self.emitters_receivers[emitter_receiver_name] = EmitterReceiver(
                status_receiver,
                self.emitters_receivers[emitter_receiver_name]["receiver_pin"],
                self.emitters_receivers[emitter_receiver_name]["pull_up_down"],
                emitter_power_pin,
            )

        threading.Thread.__init__(self)
        self.start()
        status_receiver.collect(
            status_receiver.capture_local_details.get_location(self),
            "started",
            status_receiver.Types.INITIALIZATIONS,
        )

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            for emitter_receiver_name in self.emitters_receivers:
                time.sleep(self.poll_interval)
                change, value = self.emitters_receivers[
                    emitter_receiver_name
                ].get_change()
                if change:
                    self.async_data_callback(emitter_receiver_name, value)


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

    def __init__(self):
        pass

    def collect(self, *args):
        pass

def data_callback(name, current_value):
    print(current_value)

def make_r(er_data):
    return EmittersReceivers(
            Status_Receiver_Stub(),
            er_data,
            poll_interval=0.25,
            async_data_callback = data_callback,
        )

