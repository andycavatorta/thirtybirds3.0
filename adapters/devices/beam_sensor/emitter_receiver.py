"""
---------------------------


"""

import os
import sys

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
        emitter_power_pin=-1,
        pull_up_down=0,
        poll_interval=0,
        async_data_callback=lambda x: None,
    ):
        """
        to do: finish docstring
        """
        self.receiver_pin = receiver_pin
        self.status_receiver = status_receiver
        self.async_data_callback = async_data_callback
        self.emitter_power_pin = emitter_power_pin

        self.binary_input = binary_input.Input(
            receiver_pin,
            status_receiver,
            async_data_callback,
            pull_up_down,
            poll_interval,
        )
        self.control_emitter_power = emitter_power_pin > -1
        if self.control_emitter_power:
            self.emitter_power = output.Output(emitter_power_pin, status_receiver)
        status_receiver.collect(
            status_receiver.capture_local_details.get_location(self),
            "started",
            status_receiver.types.INITIALIZATIONS,
        )

    def set_emitter_power(self, power_bool):
        """
        to do: finish docstring
        """
        if self.control_emitter_power:
            self.emitter_power.set_value(power_bool)

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

def data_callback(current_value):
    print(current_value)

def make_r(recv_pin)
    return EmitterReceiver(
            Status_Receiver_Stub(),
            recv_pin,
            1,
            0.25,
            data_callback,
        )


def make_er(recv_pin, emit_pin)
    return EmitterReceiver(
            Status_Receiver_Stub(),
            recv_pin,
            emit_pin,
            1,
            0.25,
            data_callback,
        )
