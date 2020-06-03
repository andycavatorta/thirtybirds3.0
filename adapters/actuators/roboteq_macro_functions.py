#!/usr/bin/python

import importlib
import os
import queue
import sys
import threading
import time

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions
from thirtybirds3.adapters.actuators roboteq_command_wrapper import Controllers as roboteq_command_wrapper_controller


class Controllers(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(
            self,
            app_data_receiver, 
            app_status_receiver, 
            app_exception_receiver, 
            settings_for_boards,
            settings_for_motors
        )
        self.app_status_receiver = app_status_receiver
        self.queue = queue.Queue()

        self.controllers = roboteq_command_wrapper_controller(
            app_data_receiver, 
            app_status_receiver, 
            app_exception_receiver, 
            settings_for_boards,
            settings_for_motors
        )

        self.start()

    def 





    def add_to_queue(self, message):
        self.queue.put(message)

    def run(self):
        while True:
            message = self.queue.get(True)











class Roboteq_Data_Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.start()

    def add_to_queue(self, message):
        self.queue.put(message)

    def run(self):
        while True:
            message = self.queue.get(True)
            print("data",message)
            if "internal_event" in message:
                do_tests()
# 
roboteq_data_receiver = Roboteq_Data_Receiver()

controllers = roboteq_command_wrapper.Controllers(
    roboteq_data_receiver.add_to_queue, 
    # tb.status_receiver, 
    tb.exception_receiver, 
    settings.Roboteq.BOARDS,
    settings.Roboteq.MOTORS
)

def do_tests():
    for board_name in controllers.boards:
        controllers.boards[board_name].set_serial_data_watchdog(0)
    controllers.motors["pitch_slider"].go_to_speed_or_relative_position(200)
    controllers.motors["bow_position_slider"].go_to_speed_or_relative_position(200)
    controllers.motors["bow_height"].go_to_speed_or_relative_position(200)
    controllers.motors["bow_rotation"].go_to_speed_or_relative_position(200)
    time.sleep(5)
    controllers.motors["pitch_slider"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_position_slider"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_height"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_rotation"].go_to_speed_or_relative_position(00)
    time.sleep(5)
    controllers.motors["pitch_slider"].go_to_speed_or_relative_position(-200)
    controllers.motors["bow_position_slider"].go_to_speed_or_relative_position(-200)
    controllers.motors["bow_height"].go_to_speed_or_relative_position(-200)
    controllers.motors["bow_rotation"].go_to_speed_or_relative_position(-200)
    time.sleep(5)
    controllers.motors["pitch_slider"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_position_slider"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_height"].go_to_speed_or_relative_position(0)
    controllers.motors["bow_rotation"].go_to_speed_or_relative_position(0)
    time.sleep(5)




class Macro_Functions:
    def __init__(
        self,
        app_data_receiver, 
        status_receiver, 
        exception_receiver, 
        settings_BOARDS,
        settings_MOTORS,
    ):
        self.app_data_receiver = app_data_receiver
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.settings_BOARDS = settings_BOARDS
        self.settings_MOTORS = settings_MOTORS

        ##############################################
        #    CREATE CONTROLLERS                      #
        ##############################################
        self.controllers = roboteq_command_wrapper.Controllers(
            roboteq_data_receiver.add_to_queue, 
            tb.status_receiver, 
            tb.exception_receiver, 
            settings.Roboteq.BOARDS,
            settings.Roboteq.MOTORS
        )

        ##############################################
        #    LIMIT SWITCHES                          #
        ##############################################
        GPIO.setmode(GPIO.BCM)
        for motor_name, motor_setting in settings_MOTORS.items():
            if "limit_switch_pin" in motor_setting and "limit_switch_direction" in motor_setting:
                setattr(self.controllers.motors[motor_name], "limit_switch_pin", motor_setting["limit_switch_pin"])
                setattr(self.controllers.motors[motor_name], "limit_switch_direction", motor_setting["limit_switch_direction"])
                GPIO.setup(motor_setting["limit_switch_pin"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def data_receiver(self, msg):
        pass


    def go_to_limit_switch(self, motor_name, direction=0):
        # send status message confirming process started
        # get reference to motor

        # read and record initial motor mode
        # read and record initial deceleration setting
        # read and record initial speed setting
        # set motor mode to closed loop speed
        # set speed low
        # check state of switch
        # start motion in direction
        # read motor current 
        # loop 
            # read motor current, position, and limit switch
            # when limit switch triggers or position stops changing or current spikes
                # stop motor
                # set encoder to zero or adjusted near-zero value
        # restore initial deceleration setting
        # restore initial speed setting
        # restore initial motor mode
        # send status message confirming process finished

        motor = self.controllers.motors[motor_name]

