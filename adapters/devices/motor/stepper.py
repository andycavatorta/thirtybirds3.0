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
    stepper.set_zero()
    stepper.set_zero(2349)

    stepper.move_by(400) #pulses
    stepper.move_by(400, stepper.PULSES) #pulses
    stepper.move_by(90, stepper.DEGREES) #degrees
    stepper.move_by(100, stepper.GRADS) #grads
    stepper.move_by(100, stepper.RADIANS) #radians

    stepper.move_to(400) #pulses
    stepper.move_to(400, stepper.PULSES)
    stepper.move_to(90, stepper.DEGREES)
    stepper.move_to(100, stepper.GRADS)
    stepper.move_to(100, stepper.RADIANS)

    stepper.move_to(400, stepper.PULSES, cumulative=True)
    stepper.move_to(90, stepper.DEGREES, cumulative=False)
    stepper.move_to(100, stepper.GRADS, cumulative=True)
    stepper.move_to(100, stepper.RADIANS, cumulative=False)

    get_pulses_per_revolution()
    get_positive_is_clockwise()
    def set_holding_force(enable_bool)
    def get_holding_force()
    def set_seconds_per_revolution(seconds_per_revolution)
    def get_seconds_per_revolution()

    default unit for all functions is PULSE

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


class Stepper(threading.Thread):
    def __init__(
        self,
        exception_receiver,
        event_receiver,
        direction_pin,
        pulse_pin,
        enable_pin,
        pulses_per_revolution,
        seconds_per_revolution,
        positive_is_clockwise=True,
        name=None,
    ):
        threading.Thread.__init__(self)
        ### S C O P E   P A R A M S   T O   S E L F ###
        self.exception_receiver = exception_receiver
        self.event_receiver = event_receiver
        self.pulses_per_revolution = pulses_per_revolution
        self.positive_is_clockwise = positive_is_clockwise
        self.name = self.__class__.__name__ if name is None else name

        ### T H R E A D - S P A N N i N G   V A R S  &  L O C K S ###
        self.command_queue = queue.Queue()
        self.start()

        # used to control speed. inaccuract becasuse this isn't a real-time OS
        self.seconds_per_revolution = seconds_per_revolution
        self.seconds_per_revolution_lock = threading.Lock()

        # direction is defined as positive or negative, these are converted to clockwise or counterclockwise
        #    based on the value of self.positive_is_clockwise
        self.direction = direction_names.POSITIVE
        self.direction_lock = threading.Lock()

        self.enable = False
        self.enable_lock = threading.Lock()

        # this is the only counter for motor position. all other postion values are calculated from this.
        #     its units are pulses. it does not reset on each revolution of the motor.
        self.cumulative_distance = 0
        self.cumulative_distance_lock = threading.Lock()

        self.zeroed = False
        self.zeroed_lock = threading.Lock()

        self.fault_flag = False
        self.fault_flag_lock = threading.Lock()

        self.rotary_unit_converter = unit_names.Rotary_Unit_Converter(
            self.pulses_per_revolution
        )
        self.rotary_distance_to_orientation_converter = (
            unit_names.Rotary_Distance_To_Orientation_Converter(
                self.pulses_per_revolution
            )
        )

        ### C R E A T E   O U T P U T S ###
        self.direction_output = binary_output.Output(
            direction_pin, self.exception_receiver
        )
        self.pulse_output = binary_output.Output(pulse_pin, self.exception_receiver)
        self.enable_output = binary_output.Output(enable_pin, self.exception_receiver)

        ### S T R I N G   C O N S T A N T S ###
        self.MOVE_BY = "MOVE_BY"
        self.MOVE_TO = "MOVE_TO"
        self.ROTATION = "ROTATION"
        self.DISTANCE = "DISTANCE"

        self.update_pulse_interval()

    #####################
    ### P R I V A T E ###
    #####################

    def __get_cumulative_distance(self):
        with self.cumulative_distance_lock:
            cumulative_distance = self.cumulative_distance
        return cumulative_distance

    def __set_cumulative_distance(self, cumulative_distance):
        with self.cumulative_distance_lock:
            self.cumulative_distance = cumulative_distance

    def __calculate_distance_summary(self):
        cumulative_distance = self.__get_cumulative_distance()
        orientation_pulses = self.rotary_distance_to_orientation_converter.convert(
            cumulative_distance, unit_names.PULSES
        )
        orientation_degrees = self.rotary_unit_converter.convert(
            orientation_pulses, unit_names.PULSES, unit_names.DEGREES
        )
        return (cumulative_distance, orientation_pulses, orientation_degrees)

    def __set_direction(self, direction):
        # direction should be [direction_names.POSITIVE|direction_names.NEGATIVE]
        self.direction = direction

        # set pin state
        if direction == direction_names.POSITIVE:
            pin_state = self.positive_is_clockwise
        else:  # direction == direction_names.NEGATIVE
            pin_state = not self.positive_is_clockwise

        self.direction_output.set_value(pin_state)

    def __pulse(self):
        # don't move if fault flag is engaged.
        with self.fault_flag_lock:
            if self.fault_flag is True:
                return

        # move one pulse
        self.pulse_output.set_value(False)
        time.sleep(self.pulse_interval / 2)
        self.pulse_output.set_value(True)
        time.sleep(self.pulse_interval / 2)

        # update position
        if self.direction == direction_names.POSITIVE:
            self.__set_cumulative_distance(self.__get_cumulative_distance() + 1)
        else:  # self.direction == direction_names.NEGATIVE
            self.__set_cumulative_distance(self.__get_cumulative_distance() - 1)

        # send position update
        self.event_receiver(
            self.name, event_names.MOTION_UPDATE, self.__calculate_distance_summary()
        )

    def __move_to(self, params):
        quantity, units, direction, rotation_or_distance = params
        destination_in_steps = self.rotary_unit_converter.convert(
            quantity, units, unit_names.PULSES
        )
        # calculate distance and direction
        cumulative_distance = self.__get_cumulative_distance()

        # optional parameter "direction" is ignored in this case
        if rotation_or_distance == self.DISTANCE:
            cumulative_distance = self.__get_cumulative_distance()
            delta_distance = destination_in_steps - cumulative_distance
            self.__move_by((delta_distance, unit_names.PULSES))

        if rotation_or_distance == self.ROTATION:
            current_orientation_in_steps = (
                self.rotary_distance_to_orientation_converter.convert(
                    cumulative_distance, unit_names.PULSES
                )
            )
            # current_orientation_in_steps = cumulative_distance % self.pulses_per_revolution
            # the proposed destination may all need to be normalized to within one revolunamestion
            # destination_in_steps = destination_in_steps % self.pulses_per_revolution
            destination_in_steps = (
                self.rotary_distance_to_orientation_converter.convert(
                    destination_in_steps, unit_names.PULSES
                )
            )

            if current_orientation_in_steps == destination_in_steps:
                distance_positive = 0
                distance_negative = 0

            if current_orientation_in_steps > destination_in_steps:
                distance_positive = (
                    self.pulses_per_revolution
                    + destination_in_steps
                    - current_orientation_in_steps
                )
                distance_negative = -(
                    current_orientation_in_steps - destination_in_steps
                )

            if current_orientation_in_steps < destination_in_steps:
                distance_positive = destination_in_steps - current_orientation_in_steps
                distance_negative = -(
                    self.pulses_per_revolution
                    + current_orientation_in_steps
                    - destination_in_steps
                )

            match direction:
                case direction_names.POSITIVE:
                    self.__move_by((distance_positive, unit_names.PULSES))
                case direction_names.NEGATIVE:
                    self.__move_by((distance_negative, unit_names.PULSES))
                case direction_names.SHORTEST_PATH:
                    if abs(distance_positive) > abs(distance_negative):
                        self.__move_by((distance_negative, unit_names.PULSES))
                    else:
                        self.__move_by((distance_positive, unit_names.PULSES))

    def __move_by(self, quantity_units):
        quantity, units = quantity_units
        self.__set_direction(
            direction_names.CLOCKWISE
            if quantity >= 0
            else direction_names.COUNTER_CLOCKWISE
        )
        steps = self.rotary_unit_converter.convert(quantity, units, unit_names.PULSES)

        self.event_receiver(
            self.name, event_names.MOTION_START, self.__calculate_distance_summary()
        )

        for step in range(steps):
            self.__pulse()

        self.event_receiver(
            self.name, event_names.MOTION_END, self.__calculate_distance_summary()
        )

    ###################
    ### P U B L I C ###
    ###################

    def set_fault_flag(self, fault):
        # prevent an exception loop
        with self.fault_flag_lock:
            if self.fault_flag == fault:
                return
        if fault is True:
            self.set_enable(False)
        with self.fault_flag_lock:
            self.fault_flag = fault

    def set_zero(self, offset=0, unit=unit_names.PULSES):
        # to do: check if offset sign should be inverted
        print("set_zero", offset, unit)
        pulses = self.rotary_unit_converter.convert(offset, unit, unit_names.PULSES)
        print("set_zero", pulses)
        self.__set_cumulative_distance(pulses)
        print("set_zero")

    def set_enable(self, enable_bool):
        self.enable_output.set_value(0 if enable_bool else 1)
        with self.enable_lock:
            self.enable = enable_bool

    def set_seconds_per_revolution(self, seconds_per_revolution):
        """
        to do: finish docstring
        """
        with self.seconds_per_revolution_lock:
            self.seconds_per_revolution = seconds_per_revolution
        self.update_pulse_interval()

    def get_seconds_per_revolution(self):
        """
        to do: finish docstring
        """
        with self.seconds_per_revolution_lock:
            seconds_per_revolution = self.seconds_per_revolution
        return seconds_per_revolution

    def update_pulse_interval(self):
        """
        to do: finish docstring
        """
        with self.seconds_per_revolution_lock:
            self.pulse_interval = float(self.seconds_per_revolution) / float(
                self.pulses_per_revolution
            )

    def get_position(
        self,
        units=unit_names.PULSES,
        rotation_or_distance=None,
    ):
        rotation_or_distance = (
            self.ROTATION if rotation_or_distance is None else rotation_or_distance
        )
        distance = self.__get_cumulative_distance()
        if rotation_or_distance == self.ROTATION:
            distance = self.rotary_distance_to_orientation_converter.convert(
                distance, unit_names.PULSES
            )
        return self.rotary_unit_converter.convert(distance, unit_names.PULSES, units)

    def move_by(self, quantity, units=unit_names.PULSES, asyncronous=False):
        if asyncronous is True:
            self.add_to_command_queue(self.MOVE_BY, (quantity, units))
        else:
            self.__move_by((quantity, units))

    def move_to(
        self,
        quantity,
        units=unit_names.PULSES,
        direction=direction_names.SHORTEST_PATH,
        rotation_or_distance=None,
        asyncronous=False,
    ):
        rotation_or_distance = (
            self.ROTATION if rotation_or_distance is None else rotation_or_distance
        )
        if asyncronous is True:
            self.add_to_command_queue(
                self.MOVE_TO, (quantity, units, direction, rotation_or_distance)
            )
        else:
            self.__move_by((quantity, units))
            #self.__move_by((quantity, units, direction, rotation_or_distance))

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
            if command == self.MOVE_BY:
                self.__move_by(content)
            if command == self.MOVE_TO:
                self.__move_to(content)
