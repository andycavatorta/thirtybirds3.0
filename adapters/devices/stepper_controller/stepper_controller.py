"""
---------------------------
add subsystem with Input for z-index
add subsystem with encoder
---------------------------
usage:
import Stepper_Controller from adapters.devices.stepper_controller.controller
my_motor = Stepper_Controller(
    pulses_per_revolution = 800,
    positive_is_clockwise = False
)
my_motor.set_zero()
my_motor.set_zero(-100)

"""

import queue
import os
import sys
import threading
import time


sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "binary_output"))
)

import output


NAME = __name__


class Position:
    """
    to do: finish docstring
    """
    def __init__(self, settings, name, pulses_per_revolution, position=0, callback=None):
        """
        to do: finish docstring
        """
        self.settings = settings
        self.name = name
        self.pulses_per_revolution = pulses_per_revolution
        self.position = position
        self.callback = callback
        self.position_lock = threading.Lock()

    def send_callback(self, event_type):
        return
        if self.callback is not None:
            self.callback(
                self.name,
                event_type,
                self.get_degrees_orientation(),
                self.get_steps_orientation(),
                self.get_steps_cumulative(),
            )

    def translate_steps_to_degrees(self, steps):
        """
        to do: finish docstring
        """
        return float(steps) / float(self.pulses_per_revolution) * 360.0

    def translate_degrees_to_steps(self, degrees):
        """
        to do: finish docstring
        """
        print("translate_degrees_to_steps degrees", degrees)
        print("translate_degrees_to_steps self.pulses_per_revolution", self.pulses_per_revolution)
        print("translate_degrees_to_steps formula 1", degrees / 360.0 * float(self.pulses_per_revolution))
        print("translate_degrees_to_steps formula 2", int(degrees / 360.0 * float(self.pulses_per_revolution)))
        return int(degrees / 360.0 * float(self.pulses_per_revolution))

    def set_zero(self):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position = 0
        self.send_callback(self.settings.EventTypes.MOTION_UPDATE)

    def set_zero_degrees(self):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position = 0
        self.send_callback(self.settings.EventTypes.MOTION_UPDATE)

    def increment(self, steps=1):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position += steps
        self.send_callback(self.settings.EventTypes.MOTION_UPDATE)

    def decrement(self, steps=1):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position -= steps
        self.send_callback(self.settings.EventTypes.MOTION_UPDATE)

    def set_steps_orientation(self, position):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position = position % self.pulses_per_revolution
        self.send_callback(self.settings.EventTypes.MOTION_UPDATE)

    def get_steps_orientation(self):
        """
        to do: finish docstring
        """
        return self.position % self.pulses_per_revolution

    def set_steps_cumulative(self, position):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position = position
        self.send_callback(self.settings.EventTypes.MOTION_UPDATE)

    def get_steps_cumulative(self):
        """
        to do: finish docstring
        """
        return self.position

    def set_degrees_orientation(self, degrees):
        """
        to do: finish docstring
        """
        self.set_steps_orientation(self.translate_degrees_to_steps(degrees))

    def get_degrees_orientation(self):
        """
        to do: finish docstring
        """
        return self.translate_steps_to_degrees(self.get_steps_orientation())

    def set_degrees_cumulative(self, degrees):
        """
        to do: finish docstring
        """
        self.set_steps_cumulative(self.translate_degrees_to_steps(degrees))

    def get_degrees_cumulative(self):
        """
        to do: finish docstring
        """
        return self.translate_steps_to_degrees(self.position)

    def calculate_steps_to_target_orientation(self, target_orientation, direction):
        """
        to do: finish docstring
        """

        def calculate_clockwise_distance(start, end):
            print("calculate_clockwise_distance start, end", start, end)
            if end == start:
                return 0
                print("-- equal", 0)
            if end > start:
                print("-- end > start>", start - end)
                return end - start
            else:
                print("-- end < start>", (self.pulses_per_revolution - start) + end)
                return (self.pulses_per_revolution - start) + end

        def calculate_counter_clockwise_distance(start, end):
            return -((start - end) + 0 if end > start else self.pulses_per_revolution)

        def calculate_shortest_distance(start, end):
            return min(
                calculate_clockwise_distance(start, end),
                abs(calculate_counter_clockwise_distance(start, end)),
            )

        current_orientation = self.get_steps_orientation()
        print("calculate_steps_to_target_orientation current_orientation", current_orientation)
        print("calculate_steps_to_target_orientation direction", direction)
        match (direction):
            case self.settings.Directions.CLOCKWISE:
                return calculate_clockwise_distance(
                    current_orientation, target_orientation
                )
            case self.settings.Directions.SHORTEST:
                return calculate_shortest_distance(
                    current_orientation, target_orientation
                )
            case self.settings.Directions.COUNTER_CLOCKWISE:
                return calculate_clockwise_distance(
                    current_orientation, target_orientation
                )

    def calculate_steps_to_target_cumulative(self, target_cumulative):
        """
        to do: finish docstring
        """
        return target_cumulative - self.position


class Controller(threading.Thread):
    """
    to do: finish docstring
    """

    def __init__(
        self,
        status_receiver,
        exception_receiver,
        settings,
        name,
        direction_pin,
        pulse_pin,
        enable_pin,
        pulses_per_revolution,
        callback=None,
        seconds_per_revolution=40,
        positive_is_clockwise=True,
    ):

        print("")
        print("pulse_pin",pulse_pin)
        print("direction_pin",direction_pin)
        print("enable_pin",enable_pin)
        print("")

        threading.Thread.__init__(self)
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.settings = settings
        self.command_queue = queue.Queue()
        self.interrupt_queue = queue.Queue()
        self.name = name
        self.callback = callback

        # motor properties
        self.pulses_per_revolution = pulses_per_revolution
        self.positive_is_clockwise = positive_is_clockwise

        # gpios
        self.direction_output = output.Output(
            status_receiver, exception_receiver, direction_pin
        )
        self.pulse_output = output.Output(
            status_receiver, exception_receiver, pulse_pin
        )
        self.enable_output = output.Output(
            status_receiver, exception_receiver, enable_pin
        )

        # motion_preferences
        self.enable = True
        self.direction = self.settings.Directions.CLOCKWISE
        self.seconds_per_revolution = seconds_per_revolution
        self.update_pulse_interval()

        # motion state
        self.position = Position(settings, name, pulses_per_revolution, callback=callback)

        # upstream connections
        self.status_receiver = status_receiver
        self.start()

        status_receiver.collect(
            status_receiver.capture_local_details.get_location(self),
            "started",
            self.status_receiver.EventTypes.INITIALIZED,
        )

    def set_callback(self, event_receiver):
        """
        There are use cases in which it's possible to add the callback only after instantiation
        """
        self.callback = event_receiver

    def set_zero(self):
        """
        to do: finish docstring
        """
        self.position.set_zero()

    def update_pulse_interval(self):
        """
        to do: finish docstring
        """
        self.pulse_interval = float(self.seconds_per_revolution) / float(
            self.pulses_per_revolution
        )

    def set_pulses_per_revolution(self, pulses_per_revolution):
        """
        to do: finish docstring
        """
        self.pulses_per_revolution = pulses_per_revolution
        self.update_pulse_interval()

    def get_pulses_per_revolution(self):
        """
        to do: finish docstring
        """
        return self.pulses_per_revolution

    def set_positive_is_clockwise(self, positive_is_clockwise):
        """
        to do: finish docstring
        """
        self.positive_is_clockwise = positive_is_clockwise

    def get_positive_is_clockwise(self):
        """
        to do: finish docstring
        """
        return self.positive_is_clockwise

    def set_holding_force(self, enable_bool):
        """
        to do: finish docstring
        """
        self.enable = enable_bool
        self.enable_output.set_value(0 if enable_bool else 1)

    def get_holding_force(self):
        """
        to do: finish docstring
        """
        return self.enable

    def set_direction(self, dir_str):
        """
        to do: finish docstring
        """
        if dir_str == self.settings.Directions.CLOCKWISE:
            self.direction = (
                self.settings.Directions.CLOCKWISE if self.positive_is_clockwise else self.settings.Directions.COUNTER_CLOCKWISE
            )
        if dir_str == self.settings.Directions.COUNTER_CLOCKWISE:
            self.direction = (
                self.settings.Directions.COUNTER_CLOCKWISE if self.positive_is_clockwise else self.settings.Directions.CLOCKWISE
            )
        self.direction_output.set_value(self.direction == self.settings.Directions.CLOCKWISE)

    def get_direction(self):
        """
        to do: finish docstring
        """
        return self.direction

    def set_seconds_per_revolution(self, seconds_per_revolution):
        """
        to do: finish docstring
        """
        self.seconds_per_revolution = seconds_per_revolution
        self.update_pulse_interval()

    def get_seconds_per_revolution(self):
        """
        to do: finish docstring
        """
        return self.seconds_per_revolution

    def pulse(self):
        """
        to do: finish docstring
        """
        self.pulse_output.set_value(False)
        time.sleep(self.pulse_interval / 2)
        self.pulse_output.set_value(True)
        time.sleep(self.pulse_interval / 2)
        if self.direction == self.settings.Directions.CLOCKWISE:
            self.position.increment()
        else:
            self.position.decrement()

    def __move_by_steps(self, steps):
        """
        to do: finish docstring
        """
        #print("__move_by_steps")
        self.set_direction(self.settings.Directions.CLOCKWISE if steps < 0 else self.settings.Directions.COUNTER_CLOCKWISE)
        #print("self.direction", self.direction)
        for step in range(steps):
            #print("step", step)
            try:
                self.interrupt_queue.get(False)
                break
            except queue.Empty:
                self.pulse()
        if self.callback is not None:
            self.position.send_callback(self.settings.EventTypes.MOTION_COMPLETE)

    def move_by_steps(self, steps, async_task=False):
        """
        to do: finish docstring
        """
        if async_task is False:
            self.__move_by_steps(steps)
        else:
            self.add_to_command_queue(self.__move_by_steps, steps)

    def __move_by_degrees(self, degrees):
        """
        to do: finish docstring
        """
        self.set_direction(self.settings.Directions.CLOCKWISE if degrees < 0 else self.settings.Directions.COUNTER_CLOCKWISE)
        steps = self.position.translate_degrees_to_steps(degrees)
        for step in range(steps):
            try:
                self.interrupt_queue.get(False)
                break
            except queue.Empty:
                self.pulse()
        if self.callback is not None:
            self.position.send_callback(self.settings.EventTypes.MOTION_COMPLETE)


    def move_by_degrees(self, degrees, async_task=False):
        """
        to do: finish docstring
        """
        if async_task is None:
            self.__move_by_steps(degrees)
        else:
            self.add_to_command_queue(self.__move_by_degrees, degrees)

    def move_to_step_orientation(
        self,
        target_orientation,
        direction=None,
        async_task=False
    ):
        """
        to do: finish docstring
        """
        if direction is None:
            direction = self.settings.Directions.SHORTEST

        distance = self.position.calculate_steps_to_target_orientation(
            target_orientation, direction
        )
        self.move_by_steps(distance, async_task)

    def move_to_step_cumulative(self, target_orientation, async_task=False):
        """
        to do: finish docstring
        """
        distance = self.position.calculate_steps_to_target_cumulative(
            target_orientation
        )
        self.move_by_steps(distance, async_task)

    def move_to_degree_orientation(
        self,
        target_orientation_degrees,
        direction=None,
        async_task=False
    ):
        """
        to do: finish docstring
        """
        if direction is None:
            direction = self.settings.Directions.SHORTEST
        target_orientation_steps = self.position.translate_degrees_to_steps(
            target_orientation_degrees
        )
        distance = self.position.calculate_steps_to_target_orientation(
            target_orientation_steps, direction
        )
        self.move_by_steps(distance, async_task)

    def move_to_degree_cumulative(self, target_orientation_degrees, async_task=False):
        """
        to do: finish docstring
        """
        target_orientation_steps = self.position.translate_degrees_to_steps(
            target_orientation_degrees
        )
        distance = self.position.calculate_steps_to_target_cumulative(
            target_orientation_steps
        )
        self.move_by_steps(distance, async_task)

    def cancel_movement(self):
        """
        to do: finish docstring
        """
        self.add_to_interrupt_queue()
        self.status_receiver.collect(
            self.status_receiver.capture_local_details.get_location(self),
            "started",
            self.status_receiver.EventTypes.INITIALIZED,
        )

    def add_to_interrupt_queue(self):
        """
        to do: finish docstring
        """
        self.interrupt_queue.put(True)

    def add_to_command_queue(self, command, quantity):
        """
        to do: finish docstring
        """
        self.command_queue.put((command, quantity))

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            command, quantity = self.command_queue.get(True)
            if command == self.move_by_steps:
                self.__move_by_steps(quantity)
            if command == self.__move_by_degrees:
                self.__move_by_degrees(quantity)


###############
### T E S T ###
###############

"""
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


def make_controller(
    name,
    direction_pin,
    pulse_pin,
    enable_pin,
    pulses_per_revolution,
):
    return Controller(
        Status_Receiver_Stub(),
        exception_callback,
        name,
        direction_pin,
        pulse_pin,
        enable_pin,
        pulses_per_revolution,
    )
"""
