"""
to do: finish docstring
"""

try:
    from RPi import GPIO
except ImportError:
    from Mock import GPIO

GPIO.setmode(GPIO.BCM)

class Output:
    """
    to do: finish docstring
    """
    def __init__(
            self,
            gpio,
            status_receiver
        ):
        """
        to do: finish docstring
        """
        GPIO.setup(gpio, GPIO.OUT)
        self.last_value = None
        status_receiver.collect(status_receiver.capture_local_details.get_location(self),"started",status_receiver.Types.INITIALIZATIONS)

    def set_value(self,value):
        """
        to do: finish docstring
        """
        self.last_value = value
        return GPIO.output(value)

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

    def get_location(self, *args)

class Status_Receiver_Stub:
    self.catprure_local_details = CaptureLocalDetails()

    class types:
        INITIALIZATIONS = "INITIALIZATIONS"

    def __init__(self):
        pass

    def collect(self, *args):
        pass


output = None
def make_output(pin):
    global output
    output = Output(
        pin,
        Status_Receiver_Stub()
    )
