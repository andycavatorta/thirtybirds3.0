"""
to do: finish docstring
"""

import threading
import time

try:
    from RPi import GPIO
except ImportError:
    from Mock import GPIO

GPIO.setmode(GPIO.BCM)


class Input(threading.Thread):
    """
    to do: finish docstring
    """

    def __init__(
        self,
        gpio,
        status_receiver,
        data_callback=lambda x: None,
        pull_up_down=0,
        poll_interval=0,
    ):
        """
        to do: finish docstring
        """
        self.gpio = gpio
        self.data_callback = data_callback
        self.poll_interval = poll_interval
        match pull_up_down:
            case -1:
                GPIO.setup(self.gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            case 0:
                GPIO.setup(self.gpio, GPIO.IN)
            case 1:
                GPIO.setup(self.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if poll_interval > 0:
            self.last_value = self.get_value()
            self.data_callback(self.last_value)
            threading.Thread.__init__(self)
            self.start()
        status_receiver.collect(
            status_receiver.capture_local_details.get_location(self),
            "started",
            status_receiver.types.INITIALIZATIONS,
        )

    def get_value(self):
        """
        to do: finish docstring
        """
        return GPIO.input(self.gpio)

    def get_change(self):
        """
        to do: finish docstring
        """
        current_value = self.get_value()
        if current_value != self.last_value:
            self.last_value = current_value
            return (True, current_value)
        return (False, current_value)

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            time.sleep(self.poll_interval)
            current_value = self.get_value()
            if current_value != self.last_value:
                self.data_callback(current_value)
                self.last_value = current_value





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

#up_down = [-1, 0, 1]

def test(pin, up_down):
    return Input(
            pin,
            Status_Receiver_Stub(),
            data_callback,
            up_down,
            poll_interval=0.5
    )
"""
