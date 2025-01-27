"""
The encoder is used to

    set the zero postion in the motor driver
        synchronous

    detect missed steps during motion

    confirm position after motion

can the motion confirmation event-driven by a callback
    from the stepper controller on each step?

the encoder and stepper controller report orientation in their native PPR.

alignment of two orientations is checked against a threshold of misalignment (deg)

limitations:
needs to support more than one types of absolute encoder
doesn't support all arguments for encoder or controller

"""
import os
import sys
import threading

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "devices"))
)

# to do: add simple way to choose absolute encoder library
from rotary_encoder import cui_amt_203
from stepper_controller import stepper_controller

NAME = __name__


class StepperControllerAndAbsoluteEncoder:
    """
    to do: finish docstring
    """

    def __init__(
        self,
        status_receiver,
        exception_receiver,
        event_receiver,
        settings,
        name,
        encoder_chip_select_pin,
        encoder_positions_per_revolution,
        controller_direction_pin,
        controller_pulse_pin,
        controller_enable_pin,
        controller_positions_per_revolution,
        controller_seconds_per_revolution,
        controller_positive_is_clockwise=True,
        encoder_polling_interval=0.1,
        misalignment_threshold=3,  # degrees
    ):


        self.settings = settings
        self.event_receiver = event_receiver
        self.misalignment_threshold = misalignment_threshold
        self.initialized = False

        self.controller = stepper_controller.Controller(
            status_receiver,
            exception_receiver,
            settings,
            name,
            controller_direction_pin,
            controller_pulse_pin,
            controller_enable_pin,
            controller_positions_per_revolution,
            self.__controller_callback,
            controller_seconds_per_revolution,
            controller_positive_is_clockwise,
        )

        self.encoder = cui_amt_203.Encoder(
            status_receiver,
            exception_receiver,
            name,
            encoder_chip_select_pin,
            encoder_positions_per_revolution,
            self.__encoder_callback,
            encoder_polling_interval,
        )
        self.get_position = self.encoder.get_position
        self.get_position_degrees = self.encoder.get_position_degrees
        self.set_controller_positive_is_clockwise = (
            self.controller.set_positive_is_clockwise
        )
        self.set_holding_force = self.controller.set_holding_force
        self.set_direction = self.controller.set_direction
        self.set_seconds_per_revolution = self.controller.set_seconds_per_revolution
        self.move_by_steps = self.controller.move_by_steps
        self.move_by_degrees = self.controller.move_by_degrees
        self.move_to_step_orientation = self.controller.move_to_step_orientation
        self.move_to_step_cumulative = self.controller.move_to_step_cumulative
        self.move_to_degree_orientation = self.controller.move_to_degree_orientation
        self.move_to_degree_cumulative = self.controller.move_to_degree_cumulative
        self.cancel_movement = self.controller.cancel_movement
        self.last_controller_orientation_lock = threading.Lock()
        self.zero()
        with self.last_controller_orientation_lock:
            self.last_controller_orientation_degrees = (
                self.controller.position.get_degrees_orientation()
            )
        self.initialized = True

    def get_encoder_presence(self):
        return self.encoder.get_presence()

    def set_encoder_zero(self):
        return self.encoder.set_zero()

    def zero(self):
        self.controller.position.set_degrees_orientation(self.encoder.get_position_degrees())

    def __controller_callback(
        self,
        name,
        event_type,
        degrees_orientation,
        steps_orientation,
        steps_cumulative,
    ):
        with self.last_controller_orientation_lock:
            self.last_controller_orientation_degrees = degrees_orientation
        if event_type == self.settings.EventTypes.MOTION_COMPLETE:
            self.event_receiver(
                name,
                event_type,
                (
                    degrees_orientation,
                    steps_orientation,
                    steps_cumulative,
                ),
            )

    def __encoder_callback(
        self,
        name,
        degrees_orientation,
        steps_orientation,
    ):
        if self.initialized:
            # to do: detect delay caused by lock
            with self.last_controller_orientation_lock:
                last_controller_orientation = float(
                    self.last_controller_orientation_degrees
                )
            if (
                abs(last_controller_orientation - degrees_orientation)
                > self.misalignment_threshold
            ):
                with self.last_controller_orientation_lock:
                    last_controller_orientation = float(
                        self.last_controller_orientation_degrees
                    )
                if (
                    abs(self.last_controller_orientation - degrees_orientation)
                    > self.misalignment_threshold
                ):
                    self.event_receiver(
                        self.name,
                        self.settings.EventTypes.MEASUREMENT_DISPARITY,
                        (degrees_orientation, last_controller_orientation),
                    )
