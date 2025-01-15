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

NAME = __name__


class Input(threading.Thread):
    """
    to do: finish docstring
    """

    def __init__(
        self,
        status_receiver,
        exception_receiver,
        pin_number,
        data_callback=lambda x: None,
        pull_up_down=0,
        poll_interval=0,
    ):
        """
        to do: finish docstring
        """
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.pin_number = pin_number
        self.data_callback = data_callback
        self.poll_interval = poll_interval
        self.pin_access_lock = threading.Lock()
        try:
            match pull_up_down:
                case -1:
                    GPIO.setup(self.pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                case 0:
                    GPIO.setup(self.pin_number, GPIO.IN)
                case 1:
                    GPIO.setup(self.pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        except Exception as e:
            self.exception_receiver(NAME, type(e))
        self.last_value = self.get_value()
        if poll_interval > 0:
            self.data_callback(self.last_value)
            threading.Thread.__init__(self)
            self.start()
        status_receiver.collect(
            status_receiver.capture_local_details.get_location(self),
            "started",
            status_receiver.Types.INITIALIZATIONS,
        )

    def get_value(self):
        """
        to do: finish docstring
        """
        try:
            with self.pin_access_lock:
                return GPIO.input(self.pin_number)
        except Exception as e:
            self.exception_receiver(NAME, type(e))
            return None

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

def make_input(pin, up_down):
    return Input(
            Status_Receiver_Stub(),
            exception_callback,
            pin,
            data_callback,
            up_down,
            poll_interval=0.5
    )

