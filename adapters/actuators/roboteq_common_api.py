#!/usr/bin/python
# -*- coding: ascii -*-

import glob
import os
import queue
import serial
import sys
import time
import threading

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions

@capture_exceptions.Class
class Board(threading.Thread):
    def __init__(self,path, add_to_controller_queue):
        threading.Thread.__init__(self)
        self.serial_device_path = path
        self.add_to_controller_queue = add_to_controller_queue
        self.mcu_id = ""
        self.queue = queue.Queue()
        self.serial = serial.Serial(
            port=self.serial_device_path,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
        )
        self.start()

    ##############################################
    #    MEMORY                                  #
    ##############################################

    def read_mcu_id(self, callback=None):
        serial_command = "?UID"
        self.add_to_queue(serial_command)

    ##############################################
    #    CLASS INTERNALS                         #
    ##############################################

    def add_mcu_id(self,mcu_id):
        self.mcu_id = mcu_id

    def add_to_queue(self, serial_command, callback=None):
        self.queue.put((serial_command, callback))

    def _readSerial(self):
        resp_char = " "
        resp_str = ""
        while ord(resp_char) != 13:
            resp_char = self.serial.read(1)
            resp_str += resp_char
        return resp_str

    def run(self):
        while True:
            serial_command, callback = self.queue.get(True)
            time.sleep(0.05)
            self.serial.write(serial_command +'\r')
            echo_str = self._readSerial() # for serial echo
            #print("echo_str=", echo_str)
            resp_str = self._readSerial()
            #self.add_to_controller_queue(self.serial_device_path, serial_command, resp_str, callback) 

@capture_exceptions.Class
class Motor(threading.Thread):
    def __init__(self,name,board,channel):
        threading.Thread.__init__(self)
        self.board = board
        self.name = name
        self.channel = channel
        self.bit_offset = self.channel * 16
        self.queue = queue.Queue()
        self.start()

    ##############################################
    #    MOTOR REAL TIME                         #
    ##############################################
    def go_to_speed_or_relative_position(self, value):
        """
        G is the main command for activating the motors. The command is a number ranging
        1000 to +1000 so that the controller respond the same way as when commanded using
        Analog or Pulse, which are also -1000 to +1000 commands. The effect of the command
        differs from one operating mode to another.
        In Open Loop Speed mode the command value is the desired power output level to be
        applied to the motor.
        In Closed Loop Speed mode, the command value is relative to the maximum speed that is
        stored in the MXRPM configuration parameter.
        In Closed Loop Position Relative and in the Closed Loop Tracking mode, the command is
        the desired relative destination position mode.
        The G command has no effect in the Position Count mode.
        In Torque mode, the command value is the desired Motor Amps relative to the Amps Limit
        configuration parameters
        """
        serial_command = "!G {} {}".format(self.channel, value)
        self.board.add_to_queue(serial_command)

    ##############################################
    #    CLASS INTERNALS                         #
    ##############################################

    def add_to_queue(self, serial_command, value, callback):
        self.queue.put((serial_command, value, callback))

    def run(self):
        while True:
            serial_command, value, callback = self.queue.get(True)

@capture_exceptions.Class
class Controllers(threading.Thread):
    def __init__(self, data_receiver, status_receiver, config, mcu_serial_device_path_patterns=['/dev/serial/by-id/usb-FTDI*','/dev/serial/by-id/usb-Roboteq*']):
        threading.Thread.__init__(self)
        self.data_receiver = data_receiver
        self.status_receiver = status_receiver
        self.config = config
        self.mcu_serial_device_path_patterns = mcu_serial_device_path_patterns
        self.queue = queue.Queue()
        self.boards = {}
        self.motors = {}
        self.motors = {}
        self.mcu_serial_device_paths = self.get_device_id_list()

        self.status_receiver("self.mcu_serial_device_paths",self.mcu_serial_device_paths)

        # create board objects and read their mcu_ids
        for mcu_serial_device_path in self.mcu_serial_device_paths:
            self.match_mcu_id(mcu_serial_device_path)
        
        self.status_receiver("self.boards",self.boards)

        # are physical boards found for all boards defined in config?
        mcu_ids_from_boards = [board.mcu_id for board in self.boards]
        mcu_ids_in_config = self.config["boards"].keys()

        if not (set(mcu_ids_from_boards).issubset(set(mcu_ids_in_config))):
            self.status_receiver("missing board", set(mcu_ids_in_config).difference(set(mcu_ids_from_boards)))
        else:
            # map mcu_ids to mcu_serial_device_paths
            device_path_by_mcu_id = {board.mcu_id:board.serial_device_path for board in self.boards}
            # create motor instances
            for motor_name in self.config["motors"]:
                self.motors[motor_name] = Motor(
                    motor_name, 
                    self.boards[device_path_by_mcu_id[self.config["motors"][motor_name][mcu_id]]],
                    self.config["motors"][motor_name][channel]
                )
            self.start()

    def get_device_id_list(self):
        matching_mcu_serial_device_paths = []
        for mcu_serial_device_path_pattern in self.mcu_serial_device_path_patterns:
            matching_mcu_serial_device_paths.extend(glob.glob(mcu_serial_device_path_pattern))
        return matching_mcu_serial_device_paths

    def match_mcu_id(self, mcu_serial_device_path):
        self.boards[mcu_serial_device_path] = Board(mcu_serial_device_path, self.add_to_queue)
        board.read_mcu_id(self._match_mcu_id)

    def _match_mcu_id(self, mcu_serial_device_path, serial_command, resp_str):
        print(mcu_serial_device_path, serial_command, resp_str)
        self.boards[mcu_serial_device_path].add_mcu_id(mcu_serial_device_path)
        # handle exceptions:
        #   not a Roboteq device
        #   no response
        #   garbled response probably doesn't throw an exception

        # search config file for matching mcu_ids

        # if match found, create Motor instances, bind to Board instance
        # store reference to this mcu in Controllers
        
    def add_to_queue(self, mcu_serial_device_path, serial_command, resp_str, callback):
        self.queue.put((mcu_serial_device_path, serial_command, resp_str, callback))

    def run(self):
        while True:
            mcu_serial_device_path, serial_command, resp_str, callback = self.queue.get(True)
            try:
                callback(mcu_serial_device_path, serial_command, resp_str)
            except TypeError:#if callback == None
                pass

@capture_exceptions.Function
def init(data_receiver, status_receiver, exception_receiver, config):
    capture_exceptions.init(exception_receiver)
    controllers = Controllers(data_receiver, status_receiver, config)
    return controllers

"""
macros
homing 
    by limit switch
    by encoder index
    by end of progress
    by current spike

report motion started
report motion target reached

report divergence from expected position/speed

sync motors

freeze all motors on error

read config from eeprom
write config to eeprom
"""