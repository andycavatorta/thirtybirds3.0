"""
Thirtybirds Style Requirements:
    Single and multiple devices
    Synchronous requests for value
    Synchronous requests for change
    Async polling and reporting
    callback for exceptions
    callback for events
    device name can be optionally set or automatically created

    devices do not use thirtybirds
    devices do not use logging
    devices do not use the settings module directly
    devices do not call fault states
"""

import inspect
import traceback

try:
    from RPi import GPIO
except ImportError:
    from Mock import GPIO


class Output:
    def __init__(self, pin_number, exception_receiver, device_name=None):
        ### S C O P I N G ###
        self.pin_number = pin_number
        self.exception_receiver = exception_receiver
        self.last_value = None
        self.device_name = (
            f"{self.__class__.__name__}_{pin_number}"
            if device_name is None
            else device_name
        )

        ### G P I O   S T U F F ###
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        try:
            GPIO.setup(pin_number, GPIO.OUT)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            #print(decorator_self.__class__.__name__, function_ref.__name__)
            exception_details = {
                "script_name":__file__,
                "class_name":self.__class__.__name__,
                "method_name":inspect.currentframe().f_code.co_name,
                "stacktrace":traceback.format_exception(exc_type, exc_value,exc_traceback)
            }
            self.exception_receiver("main instantiation exception", exception_details)

    def set_value(self, value):
        self.last_value = value
        try:
            GPIO.output(self.pin_number, value)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            #print(decorator_self.__class__.__name__, function_ref.__name__)
            exception_details = {
                "script_name":__file__,
                "class_name":self.__class__.__name__,
                "method_name":inspect.currentframe().f_code.co_name,
                "stacktrace":traceback.format_exception(exc_type, exc_value,exc_traceback)
            }
            self.exception_receiver(__file__, exception_details)

    def get_last_value(self):
        """
        This is used to read the last value set.
        """
        return self.last_value
