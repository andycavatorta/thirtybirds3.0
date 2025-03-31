"""
Thirtybirds Style Requirements:
    Single and multiple devices: no
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

typical usage:
    actuator.pulse()
    actuator.pulse(30)
"""

import inspect
import traceback
import queue
import os
import sys
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gpio import binary_output
import event_names
import direction_names
import unit_names

class Actuator(threading.Thread):
    def __init__(
        self,
        exception_receiver,
        event_receiver,
        output_pin,
        active_period_ms=0,
        inactive_period_ms=0,
        name=None,
    ):
        threading.Thread.__init__(self)

        ### S C O P E   P A R A M S   T O   S E L F ###
        self.exception_receiver = exception_receiver
        self.event_receiver = event_receiver
        self.output_pin = output_pin
        self.active_period_ms = active_period_ms
        self.inactive_period_ms = inactive_period_ms
        self.name = self.__class__.__name__ if name is None else name

        ### S T R I N G   C O N S T A N T S ###
        self.ENGAGE = "ENGAGE"
        self.DISENGAGE = "DISENGAGE"
        self.PULSE = "PULSE"

        ### T H R E A D - S P A N N i N G   V A R S  &  L O C K S ###
        self.command_queue = queue.Queue()
        self.start()

        ### C R E A T E   O U T P U T ###
        self.power_output = binary_output.Output(
            output_pin, self.exception_receiver
        )
        self.power_output.set_value(True)


    #####################
    ### P R I V A T E ###
    #####################

    def _pulse(self, _active_period_ms=0):
        """
        local _active_period_ms supercedes self.active_period_ms
        if both are 0, no action
        """
        print("_pulse 0")
        if _active_period_ms <= 0 and self.active_period_ms <= 0:
            # fail quietly
            return
        print("_pulse 1")
        active_period_ms = _active_period_ms if _active_period_ms > 0 else self.active_period_ms
        print("_pulse 2")
        try:
            print("_pulse 3")
            self.power_output.set_value(False)
            time.sleep(active_period_ms)
            print("_pulse 4")
            self.power_output.set_value(True)
        except Exception as e:
            print("_pulse 5")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            #print(decorator_self.__class__.__name__, function_ref.__name__)
            exception_details = {
                "script_name":__file__,
                "class_name":self.__class__.__name__,
                "method_name":inspect.currentframe().f_code.co_name,
                "stacktrace":traceback.format_exception(exc_type, exc_value,exc_traceback)
            }
            self.exception_receiver(__file__, exception_details)
        finally:
            self.power_output.set_value(True)

    ###################
    ### P U B L I C ###
    ###################

    def pulse(self, active_period_ms=0):
        self.add_to_command_queue(self.PULSE, active_period_ms)

    def engage(self):
        self.add_to_command_queue(self.ENGAGE, None)

    def disngage(self):
        self.add_to_command_queue(self.DISENGAGE, None)

    ################################
    ### T H R E A D   S T U F F  ###
    ################################

    def add_to_command_queue(self, command, content):
        """
        to do: finish docstring
        """
        self.command_queue.put((command, content))

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            command, content = self.command_queue.get(True)
            if command == self.ENGAGE:
                pass
                # to do: finish when needed
            if command == self.DISENGAGE:
                pass
                # to do: finish when needed
            if command == self.PULSE:
                self._pulse(content)
                time.sleep(self.inactive_period_ms)

