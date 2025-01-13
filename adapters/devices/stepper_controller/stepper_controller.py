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

try:
    from RPi import GPIO
except ImportError:
    from Mock import GPIO

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(
                __file__
            ),
        '..',
        'binary_output'
        )
    )
)

import output

CLOCKWISE = "CLOCKWISE"
COUNTER_CLOCKWISE = "COUNTER_CLOCKWISE"
SHORTEST = "SHORTEST"
MOTION_COMPLETE = "MOTION_COMPLETE"

GPIO.setmode(GPIO.BCM)


class Position:
    """
    to do: finish docstring
    """
    CLOCKWISE = "CLOCKWISE"
    COUNTER_CLOCKWISE = "COUNTER_CLOCKWISE"
    SHORTEST = "SHORTEST"
    MOTION_COMPLETE = "MOTION_COMPLETE"


    def __init__(self, pulses_per_revolution, position=0):
        """
        to do: finish docstring
        """
        self.pulses_per_revolution = pulses_per_revolution
        self.position = position
        self.position_lock = threading.Lock()

    def translate_steps_to_degrees(self, steps):
        """
        to do: finish docstring
        """
        return float(steps) / float(self.pulses_per_revolution) * 360.0

    def translate_degrees_to_steps(self, degrees):
        """
        to do: finish docstring
        """
        return int(degrees / 360.0 * float(self.pulses_per_revolution))

    def set_zero(self):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position = 0

    def increment(self, steps=1):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position += steps

    def decrement(self, steps=1):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position -= steps

    def set_steps_orientation(self, position):
        """
        to do: finish docstring
        """
        with self.position_lock:
            self.position = position % self.pulses_per_revolution

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
            return (end - start) + 0 if end > start else self.pulses_per_revolution

        def calculate_counter_clockwise_distance(start, end):
            return -((start - end) + 0 if end > start else self.pulses_per_revolution)

        def calculate_shortest_distance(start, end):
            return min(
                calculate_clockwise_distance(start, end),
                abs(calculate_counter_clockwise_distance(start, end)),
            )

        current_orientation = self.get_steps_orientation()
        match (direction):
            case self.CLOCKWISE:
                return calculate_clockwise_distance(
                    current_orientation, target_orientation
                )
            case self.SHORTEST:
                return calculate_shortest_distance(
                    current_orientation, target_orientation
                )
            case self.COUNTER_CLOCKWISE:
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
    CLOCKWISE = "CLOCKWISE"
    COUNTER_CLOCKWISE = "COUNTER_CLOCKWISE"
    SHORTEST = "SHORTEST"
    MOTION_COMPLETE = "MOTION_COMPLETE"


    def __init__(
        self,
        status_receiver,
        name,
        direction_pin,
        pulse_pin,
        enable_pin,
        pulses_per_revolution,
        seconds_per_revolution=40,
        positive_is_clockwise=True
    ):
        threading.Thread.__init__(self)
        self.command_queue = queue.Queue()
        self.interrupt_queue = queue.Queue()
        self.name = name

        # motor properties
        self.pulses_per_revolution = pulses_per_revolution
        self.positive_is_clockwise = positive_is_clockwise

        # gpios
        self.direction_output = output.Output(status_receiver, direction_pin)
        self.pulse_output = output.Output(status_receiver, pulse_pin)
        self.enable_output = output.Output(status_receiver, enable_pin)

        # motion_preferences
        self.enable = True
        self.direction = self.CLOCKWISE
        self.seconds_per_revolution = seconds_per_revolution
        self.update_pulse_interval()

        # motion state
        self.position = Position(pulses_per_revolution)

        # upstream connections
        self.status_receiver = status_receiver
        self.start()

        status_receiver.collect(
            status_receiver.capture_local_details.get_location(self),
            "started",
            self.status_receiver.Types.INITIALIZATIONS,
        )

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
        self.enable.set_value(enable_bool)

    def get_holding_force(self):
        """
        to do: finish docstring
        """
        return self.enable

    def set_direction(self, dir_str):
        """
        to do: finish docstring
        """
        if dir_str == self.CLOCKWISE:
            self.direction = (
                self.CLOCKWISE if self.positive_is_clockwise else self.COUNTER_CLOCKWISE
            )
        if dir_str == self.COUNTER_CLOCKWISE:
            self.direction = (
                self.COUNTER_CLOCKWISE if self.positive_is_clockwise else self.CLOCKWISE
            )

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
        self.pulse_output.sef_value(True)
        time.sleep(self.pulse_interval / 2)
        self.pulse_output.sef_value(False)
        time.sleep(self.pulse_interval / 2)
        if self.direction == self.CLOCKWISE:
            self.position.increment()
        else:
            self.position.decrement()

    def __move_by_steps(self, steps, async_callback):
        """
        to do: finish docstring
        """
        self.set_direction(self.CLOCKWISE if steps < 0 else self.COUNTER_CLOCKWISE)
        for step in range(steps):
            try:
                self.interrupt_queue.get(False)
                break
            except queue.Empty:
                self.pulse()
        if async_callback is not None:
            async_callback(self.name, MOTION_COMPLETE)

    def move_by_steps(self, steps, async_callback=None):
        """
        to do: finish docstring
        """
        if async_callback is None:
            self.__move_by_steps(steps, None)
        else:
            self.add_to_command_queue(self.__move_by_steps, steps, async_callback)

    def __move_by_degrees(self, degrees, async_callback=None):
        """
        to do: finish docstring
        """
        self.set_direction(self.CLOCKWISE if degrees < 0 else self.COUNTER_CLOCKWISE)
        steps = self.position.translate_degrees_to_steps(degrees)
        for step in range(steps):
            try:
                self.interrupt_queue.get(False)
                break
            except queue.Empty:
                self.pulse()
        if async_callback is not None:
            async_callback(self.name, MOTION_COMPLETE)

    def move_by_degrees(self, degrees, async_callback=None):
        """
        to do: finish docstring
        """
        if async_callback is None:
            self.__move_by_steps(degrees, None)
        else:
            self.add_to_command_queue(self.__move_by_degrees, degrees, async_callback)

    def move_to_step_orientation(
        self, target_orientation, direction=SHORTEST, async_callback=None
    ):
        """
        to do: finish docstring
        """
        distance = self.position.calculate_steps_to_target_orientation(
            target_orientation, direction
        )
        self.move_by_steps(distance, async_callback)

    def move_to_step_cumulative(self, target_orientation, async_callback=None):
        """
        to do: finish docstring
        """
        distance = self.position.calculate_steps_to_target_cumulative(
            target_orientation
        )
        self.move_by_steps(distance, async_callback)

    def move_to_degree_orientation(
        self, target_orientation_degrees, direction=SHORTEST, async_callback=None
    ):
        """
        to do: finish docstring
        """
        target_orientation_steps = self.position.translate_degrees_to_steps(
            target_orientation_degrees
        )
        distance = self.position.calculate_steps_to_target_orientation(
            target_orientation_steps, direction
        )
        self.move_by_steps(distance, async_callback)

    def move_to_degree_cumulative(
        self, target_orientation_degrees, async_callback=None
    ):
        """
        to do: finish docstring
        """
        target_orientation_steps = self.position.translate_degrees_to_steps(
            target_orientation_degrees
        )
        distance = self.position.calculate_steps_to_target_cumulative(
            target_orientation_steps
        )
        self.move_by_steps(distance, async_callback)

    def cancel_movement(self):
        """
        to do: finish docstring
        """
        self.add_to_interrupt_queue()
        self.status_receiver.collect(
            self.status_receiver.capture_local_details.get_location(self),
            "started",
            self.status_receiver.Types.INITIALIZATIONS,
        )

    def add_to_interrupt_queue(self):
        """
        to do: finish docstring
        """
        self.interrupt_queue.put(True)

    def add_to_command_queue(self, command, quantity, async_callback):
        """
        to do: finish docstring
        """
        self.command_queue.put((command, quantity, async_callback))

    def run(self):
        """
        to do: finish docstring
        """
        while True:
            command, quantity, async_callback = self.command_queue.get(True)
            if command == self.__move_by_steps:
                self.__move_by_steps(quantity, async_callback)
            if command == self.__move_by_degrees:
                self.__move_by_degrees(quantity, async_callback)


###############
### T E S T ###
###############


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


def make_controller(
        name,
        direction_pin,
        pulse_pin,
        enable_pin,
        pulses_per_revolution,
    ):
    return controller = Controller(
        Status_Receiver_Stub(),
        name,
        direction_pin,
        pulse_pin,
        enable_pin,
        pulses_per_revolution,
    )

"""
controller = Controller(
    name,
    direction_pin,
    pulse_pin,
    enable_pin,
    pulses_per_revolution,
    status_receiver,
    seconds_per_revolution=400,
    positive_is_clockwise=True,
)
"""

# ?????? finish writing tests
