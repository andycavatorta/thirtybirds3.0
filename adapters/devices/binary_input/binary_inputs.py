"""
This module is a generic way to read and monitor the binary states of multiple GPIO inputs.
The parameters of Switches are:
    named_gpios_d (required):{
            "A": {
                "gpio":23,
                "pull_up_down": 0,
            }
            "B": {
                "gpio":3,
                "pull_up_down": 1,
            },
            "C": {
                "gpio":13,
                "pull_up_down": -1,
            }
        }
    data_callback: function reference (required)
    status_callback: function reference (required)
    polling interval: int/float seconds (optional)
"""

import threading
import time

try:
    from RPi import GPIO
except ImportError:
    from Mock import GPIO

GPIO.setmode(GPIO.BCM)

NAME = __name__


class Inputs(threading.Thread):
    """
    to do: finish docstring
    """

    def __init__(
        self,
        status_receiver,
        exception_receiver,
        named_gpios_d,
        data_callback=lambda x: None,
        poll_interval=0,
    ):
        """
        to do: finish docstring
        """
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.named_gpios_d = named_gpios_d
        self.data_callback = data_callback
        self.poll_interval = poll_interval
        self.pin_access_lock = threading.Lock()
        for name, params in self.named_gpios_d.items():
            try:
                match params["pull_up_down"]:
                    case -1:
                        GPIO.setup(params["gpio"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                    case 0:
                        GPIO.setup(params["gpio"], GPIO.IN)
                    case 1:
                        GPIO.setup(params["gpio"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            except Exception as e:
                self.exception_receiver(NAME, type(e))
        if poll_interval > 0:
            # collect first batch of values
            for name, params in self.named_gpios_d.items():
                named_gpios_d[name]["last_value"] = self.get_value(name)
                self.data_callback([name, named_gpios_d[name]["last_value"]])
            threading.Thread.__init__(self)
            self.start()
        self.status_receiver.collect(
            "started", self.status_receiver.Types.INITIALIZATIONS
        )

    def get_value(self, name):
        """
        to do: finish docstring
        """
        try:
            with self.pin_access_lock:
                return GPIO.input(self.named_gpios_d[name]["gpio"])
        except Exception as e:
            self.exception_receiver(NAME, type(e))
        return None

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            time.sleep(self.poll_interval)
            for name in self.named_gpios_d.keys():
                current_value = self.get_value(name)
                if current_value != self.named_gpios_d[name]["last_value"]:
                    self.named_gpios_d[name]["last_value"] = self.get_value(name)
                    self.data_callback([name, self.named_gpios_d[name]["last_value"]])


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

def exception_callback(name, e):
    print(name, e)

def make_inputs(named_gpios_d):
    return Inputs(
        Status_Receiver_Stub(),
        exception_callback,
        named_gpios_d,
        data_callback,
        0.5
    )

