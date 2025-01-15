"""
to do: finish docstring
"""

try:
    from RPi import GPIO
except ImportError:
    from Mock import GPIO

GPIO.setmode(GPIO.BCM)

NAME = __name__


class Output:
    """
    to do: finish docstring
    """

    def __init__(
        self,
        status_receiver,
        exception_receiver,
        pin_number,
    ):
        """
        to do: finish docstring
        """
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.pin_number = pin_number
        self.last_value = None
        try:
            GPIO.setup(pin_number, GPIO.OUT)
        except Exception as e:
            self.exception_receiver(NAME, type(e))
        status_receiver.collect(
            status_receiver.capture_local_details.get_location(self),
            "started",
            status_receiver.Types.INITIALIZATIONS,
        )

    def set_value(self, value):
        """
        to do: finish docstring
        """
        self.last_value = value
        try:
            GPIO.output(self.pin_number, value)
        except Exception as e:
            self.exception_receiver(NAME, type(e))

    def get_last_value(self):
        """
        This is used to read the last value set.
        It's included here in case this object is used by a system that makes state hard to capture in real time.
        """
        return self.last_value


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


def exception_callback(name, e):
    print(name, e)


def make_output(pin):
    return Output(
        Status_Receiver_Stub(),
        exception_callback,
        pin,
    )

