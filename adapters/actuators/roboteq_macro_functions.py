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
from thirtybirds3.adapters.actuators import roboteq_command_wrapper

#@capture_exceptions.Class
class Controllers(threading.Thread):
    def __init__(
            self, 
            data_receiver, 
            status_receiver, 
            exception_receiver,
            boards_config, 
            motors_config, 
            mcu_serial_device_path_patterns=['/dev/serial/by-id/usb-FTDI*','/dev/serial/by-id/usb-Roboteq*']):
        threading.Thread.__init__(self)
        capture_exceptions.init(exception_receiver)
        self.data_receiver = data_receiver
        self.status_receiver = status_receiver
        self.boards_config = boards_config
        self.motors_config = motors_config
        self.mcu_serial_device_path_patterns = mcu_serial_device_path_patterns
        self.queue = queue.Queue()
        self.boards_to_device_path = {} 
        self.boards = {}
        self.motors = {}
        self.mcu_serial_device_paths = self.gxet_device_id_list()
        self.start()
        # create board objects and read their mcu_ids
        for mcu_serial_device_path in self.mcu_serial_device_paths:
            self.boards_to_device_path[mcu_serial_device_path] = roboteq_command_wrapper.Board(mcu_serial_device_path, self, self.add_to_queue)

    def match_boards_to_config(self, mcu_serial_device_path, resp_str):
        # this method verifies that all mcu_ids listed in config can be matched with discovered boards.
        # todo: this can much more terse and pythonic
        # todo: handle mismatches or incomplete processes
        mcu_ids_in_config = list(self.boards_config.keys())
        for board in self.boards_to_device_path.values():
            mcu_ids_in_config.remove(board.read_internal_mcu_id())

        if len(mcu_ids_in_config) == 0:
            for board_name in self.boards_config:
                mcu_id_from_config = self.boards_config[board_name]["mcu_id"]
                for board_object in self.boards_to_device_path.values():
                    if board_object.read_internal_mcu_id() == mcu_id_from_config:
                        self.boards[board_name] = board_object
                        break
            self.create_motors()

    def create_motors(self):
        device_path_by_mcu_id = {}
        for serial_id in self.boards:
            device_path_by_mcu_id[self.boards[serial_id].read_internal_mcu_id()] = serial_id

        for motor_name in self.motors_config:
            self.motors[motor_name] = roboteq_command_wrapper.Motor(
                motor_name,
                self.boards[device_path_by_mcu_id[self.motors_config[motor_name]["mcu_id"]]],
                self.motors_config[motor_name]["channel"],
                self.status_receiver
            )
        time.sleep(0.5)
        self.data_receiver({"internal_event":"motors_initialized"})

    def get_device_id_list(self):
        matching_mcu_serial_device_paths = []
        for mcu_serial_device_path_pattern in self.mcu_serial_device_path_patterns:
            matching_mcu_serial_device_paths.extend(glob.glob(mcu_serial_device_path_pattern))
        return matching_mcu_serial_device_paths

    def add_to_queue(self, mcu_serial_device_path, channel, method, resp_str):
        #print("-add_to_queue-",mcu_serial_device_path, channel, method, resp_str)
        self.queue.put(( mcu_serial_device_path, channel, method, resp_str))

    def run(self):
        while True:
            mcu_serial_device_path, channel, method, resp_str = self.queue.get(True)
            #print(mcu_serial_device_path, channel, method, resp_str)

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

