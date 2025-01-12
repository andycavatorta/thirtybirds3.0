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


Is this invoked by first instantiating the controller and encoder
and passing them to this system.

"""





class StepperControllerAndAbsoluteEncoder():
    """
    to do: finish docstring
    """
    def __init__(
        self,
        status_receiver,
        controller_instance,
        controller_ppr,
        encoder_instance,
        encoder_resolution,
        misalignment_threshold = 3 #degrees
    ):
        """
        to do: finish docstring
        """
        self.status_receiver = status_receiver
        self.controller_instance = controller_instance
        self.controller_ppr = controller_ppr
        self.encoder_instance = encoder_instance
        self.encoder_resolution = encoder_resolution
        self.controller_instance.add_motion_callback(self.check_alignment)
        self.misalignment_threshold = misalignment_threshold
        self.status_receiver.collect(
            "started", self.status_receiver.types.INITIALIZATIONS
        )

    def translate_controller_to_degrees(self, controller_orientation):
        """
        to do: finish docstring
        """
        pass

    def translate_encoder_to_degrees(self, encoder_orientation):
        """
        to do: finish docstring
        """
        pass

    def translate_degrees_to_controller(self, degrees):
        """
        to do: finish docstring
        """
        pass

    def translate_degrees_to_encoder(self, degrees):
        """
        to do: finish docstring
        """
        pass

    def translate_controller_to_encoder(self, controller_orientation):
        """
        to do: finish docstring
        """
        pass

    def translate_encoder_to_controller(self, encoder_orientation):
        """
        to do: finish docstring
        """
        pass

    def zero_stepper_zero(self):
        """
        to do: finish docstring
        """
        pass

    def check_alignment(self,controller_orientation):
        """
        to do: finish docstring
        """
        encoder_orientations = self.encoder_instance.get_positions()



self.misalignment_threshold


