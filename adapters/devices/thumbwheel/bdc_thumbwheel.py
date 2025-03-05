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
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gpio import binary_input
import event_names


class Thumbwheel:
    """
    create 4 inputs
    """

    def __init__(
        self,
        pin_numbers,
        exception_receiver,
        event_receiver,
        poll_interval=1,
        device_name=None,
    ):
        ### S E L F   V A R S ###
        self.pin_numbers = pin_numbers
        self.exception_receiver = exception_receiver
        self.upstream_event_receiver = event_receiver
        self.device_name = (
            self.__class__.__name__ if device_name is None else device_name
        )
        self.binary_value = 0b0000

        self.value_lock = threading.Lock()

        ### D E V I C E S ###
        binary_input.Inputs(
            {
                "one": self.pin_numbers[0],
                "two": self.pin_numbers[1],
                "four": self.pin_numbers[2],
                "eight": self.pin_numbers[3],
            },
            -1,  # values [-1,0,1] for [down, none, up]
            exception_receiver,
            self.event_receiver,
            poll_interval,
            invert_value=False,
        )

    def get_value(self):
        #with self.value_lock:
        return int(self.binary_value,2)

    def event_receiver(self, device_name, event_name, value):
        with self.value_lock:
            if event_name == event_names.CHANGE:
                match device_name:
                    case "one":
                        if value is True:
                            self.binary_value |= 1 << 0
                        else:
                            self.binary_value &= ~(1 << 0)
                    case "two":
                        if value is True:
                            self.binary_value |= 1 << 1
                        else:
                            self.binary_value &= ~(1 << 1)
                    case "four":
                        if value is True:
                            self.binary_value |= 1 << 2
                        else:
                            self.binary_value &= ~(1 << 2)
                    case "eight":
                        if value is True:
                            self.binary_value |= 1 << 3
                        else:
                            self.binary_value &= ~(1 << 3)

            self.upstream_event_receiver(
                self.device_name, event_names.CHANGE, int(self.binary_value)
            )


class Thumbwheels:
    """
    The variable pin_numbers_by_place is a nested .
    There is one outer cycle for each thumbwheel.
    These represent decimal digits starting " = " the 1s place.
    The inner cycle of each represents the gpios for BDC binary digits 0001 through 1000
    The gpios_2l for 4-digit decimal thumbwheel might look like
    [
        [
            4, #bdc binary one
            3, #bdc binary two
            2, #bdc binary fou
            1 #bdc binary eight
        ], # decimal ones
        [8,7,6,5], # decimal tens
        [11,12,15,13], # decimal hundreds
        [21,22,23,9], # decimal thousands
    ]
    """

    def __init__(
        self,
        pin_numbers_by_place,
        exception_receiver,
        event_receiver,
        poll_interval=1,
        device_name=None,
    ):
        ### S E L F   V A R S ###
        self.pin_numbers_by_place = pin_numbers_by_place
        self.exception_receiver = exception_receiver
        self.upstream_event_receiver = event_receiver
        self.poll_interval = poll_interval
        self.device_name = (
            self.__class__.__name__ if device_name is None else device_name
        )

        self.value = -1
        self.thumbwheels_by_place_name = {}

        self.value_lock = threading.Lock()

        ### D E V I C E S ###
        for index in range(len(pin_numbers_by_place)):
            #for place_name_zeros, thumbwheel_pins in pin_numbers_by_place.enumerate():
            thumbwheel_pins = pin_numbers_by_place[index]
            place_name = str(10**index)
            self.thumbwheels_by_place_name[place_name] = Thumbwheel(
                thumbwheel_pins,
                exception_receiver,
                self.event_receiver,
                1,
                place_name
            )

        #for key, ref in self.thumbwheels_by_place_name.items():
        #    print(key, ref.get_value() )

    def get_value(self):
        with self.value_lock:
            return self.value

    def event_receiver(self, device_name, event_name, value):
        """
        no matter what the changes are, request values from each Thumbwheel instance
        """
        print("thumbwheels event_receiver",device_name, event_name, value)
        total = 0
        for place_name, thumbwheel_instance in self.thumbwheels_by_place_name.items():
            print("111",place_name, thumbwheel_instance)
            place_name_int = str(place_name)
            print("222",place_name_int)
            instance_value = thumbwheel_instance.get_value() * place_name_int
            print("333",instance_value)
            total += int(instance_value)
            print("444",total)

        #with self.value_lock:
        #    self.value = total

        #self.upstream_event_receiver(self.device_name, event_names.CHANGE, total)
