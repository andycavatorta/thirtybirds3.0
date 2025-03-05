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
import threading
import time
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import event_names

try:
    from RPi import GPIO
except ImportError:
    from Mock import GPIO


class Input(threading.Thread):
    """
    to do: finish docstring
    """

    def __init__(
        self,
        # required
        pin_number,
        pull_up_down,  # values [-1,0,1] for [down, none, up]
        exception_receiver,
        # optional
        event_receiver=lambda x: None,  # needed only if polling
        poll_interval=0,  # polling happens if poll_interval > 0
        invert_value=False,
        device_name=None,
    ):
        ### S C O P I N G ###
        threading.Thread.__init__(self)
        self.exception_receiver = exception_receiver
        self.event_receiver = event_receiver
        self.poll_interval = poll_interval
        self.invert_value = invert_value
        self.pin_number = pin_number
        self.device_name = (
            f"{self.__class__.__name__}_{pin_number}"
            if device_name is None
            else device_name
        )

        self.last_value = None

        ### G P I O   S T U F F ###
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        try:
            match pull_up_down:
                case -1:
                    GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                case 0:
                    GPIO.setup(pin_number, GPIO.IN)
                case 1:
                    GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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

        ### T H R E A D   S T U F F ###
        self.pin_access_lock = threading.Lock()
        if self.poll_interval > 0:
            self.start()

    def get_value(self):
        """
        to do: finish docstring
        """
        try:
            with self.pin_access_lock:
                value = GPIO.input(self.pin_number) == 1
                self.last_value = not value if self.invert_value else value
                return self.last_value
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
            return None

    def get_change(self):
        """
        to do: finish docstring
        """
        last_value = bool(self.last_value)
        current_value = self.get_value()
        return (current_value != last_value, current_value)

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            time.sleep(self.poll_interval)
            changed, current_value = self.get_change()
            if changed:
                self.event_receiver(self.device_name, event_names.CHANGE, current_value)


class Inputs(threading.Thread):
    """
    This is useful for a range of pins with identitical configurations
    """

    def __init__(
        self,
        # required
        pin__names_and_numbers,
        pull_up_down,  # values [-1,0,1] for [down, none, up]
        exception_receiver,
        # optional
        event_receiver=lambda x: None,  # needed only if polling
        poll_interval=0,  # polling happens if poll_interval > 0
        invert_value=False,
    ):
        ### S C O P I N G ###
        self.exception_receiver = exception_receiver
        self.event_receiver = event_receiver
        self.poll_interval = poll_interval
        self.invert_value = invert_value
        self.pin__names_and_numbers = pin__names_and_numbers

        self.pins = {}
        for name, pin_number in self.pin__names_and_numbers.items():
            self.pins[name] = Input(
                pin_number,
                pull_up_down,
                exception_receiver,
                invert_value=invert_value,
                device_name=name,
            )
        if self.poll_interval > 0:
            threading.Thread.__init__(self)
            self.start()

    def get_values(self):
        """
        to do: finish docstring
        """
        # to do: replace with comprehension
        collected_values = {}
        for name in self.pins:
            collected_values[name] = self.pins[name].get_value()
        return collected_values

    def get_changes(self):
        """
        to do: finish docstring
        """
        # to do: replace with comprehension
        collected_values = {}
        for name in self.pins:
            changed, value = self.pins[name].get_change()
            if changed:
                collected_values[name] = value
                #collected_values[name] = self.pins[name].get_value()
        return collected_values

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            time.sleep(self.poll_interval)
            changes = self.get_changes()
            print("changes=========================",changes)
            for name, value in changes.items():
                self.event_receiver(name, event_names.CHANGE, value)
