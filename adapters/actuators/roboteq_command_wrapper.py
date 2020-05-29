#!/usr/bin/python

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

#@capture_exceptions.Class
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
        self.add_to_queue(serial_command, callback)

    ##############################################
    #    CLASS INTERNALS                         #
    ##############################################

    def read_internal_mcu_id(self):
        return self.mcu_id

    def add_mcu_id(self,mcu_id):
        self.mcu_id = mcu_id

    def add_to_queue(self, serial_command, callback=None):
        self.queue.put((serial_command, callback))

    def _readSerial(self):
        resp_char = " "
        resp_str = ""
        while ord(resp_char) != 13:
            resp_char = self.serial.read(1)
            #print(resp_char)
            resp_str += resp_char.decode('utf-8')
        resp_str = resp_str[:-1] # trim /r from end
        print("resp_str",resp_str)
        resp_l = resp_str.split('=')
        if len(resp_l) == 1:
            return resp_str
        else:
            return resp_l[1]
        #resp_str = resp_str.split('=')[1]
        #return resp_str[:-1]

    def run(self):
        while True:
            serial_command, callback = self.queue.get(True)
            time.sleep(0.05)
            self.serial.write(str.encode(serial_command +'\r'))
            echo_str = self._readSerial() # for serial echo
            #print("echo_str=", echo_str)
            resp_str = self._readSerial()
            #print("resp_str=", resp_str)
            #print("callback",callback)
            try:
                callback(self.serial_device_path,resp_str)
            except TypeError as e: #if callback == None
                pass
            #self.add_to_controller_queue(self.serial_device_path, serial_command, resp_str, callback)

#@capture_exceptions.Class
class Motor(threading.Thread):
    def __init__(self,name,board,channel,status_receiver):
        threading.Thread.__init__(self)
        self.board = board
        self.name = name
        self.channel = channel
        self.status_receiver = status_receiver
        self.bit_offset = self.channel * 16
        self.queue = queue.Queue()
        self.start()
        #self.status_receiver("starting motor instance", self.name)

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
    #    SAFETY                                  #
    ##############################################
    def read_fault_flags(self):
        """
        Reports the status of the controller fault conditions that can occur during operation. The
        response to that query is a single number which must be converted into binary in order to
        evaluate each of the individual status bits that compose it.

        f1 = Overheat
        f2 = Overvoltage
        f3 = Undervoltage
        f4 = Short circuit
        f5 = Emergency stop
        f6 = Brushless sensor fault
        f7 = MOSFET failure
        f8 = Default configuration loaded at startup

        FM = f1 + f2*2 + f3*4 + ... + fn*2n-1
        """
        serial_command = "?FF {}".format(self.channel)
        self.board.add_to_queue(serial_command)


    ##############################################
    #    CLASS INTERNALS                         #
    ##############################################

    def add_to_queue(self, serial_command, value, callback):
        self.queue.put((serial_command, value, callback))

    def run(self):
        while True:
            try:
                serial_command, value, callback = self.queue.get(block=True, timeout=0.5)
            except queue.Empty:
                self.read_fault_flags()


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
        self.boards = {}
        self.motors = {}
        self.mcu_serial_device_paths = self.get_device_id_list()
        #self.status_receiver("self.mcu_serial_device_paths",self.mcu_serial_device_paths)

        # create board objects and read their mcu_ids
        for mcu_serial_device_path in self.mcu_serial_device_paths:
            self.match_mcu_id(mcu_serial_device_path)
        #self.status_receiver("self.boards",self.boards)
        print("self.boards",self.boards)
        # This is brittle.  But an async method would rely on the serial timeout for each board. 
        time.sleep(5) 
        # are physical boards found for all boards defined in config?
        mcu_ids_from_boards = [board.read_internal_mcu_id() for board in self.boards.values()]
        #self.status_receiver("mcu_ids_from_boards",mcu_ids_from_boards)
        print("mcu_ids_from_boards",mcu_ids_from_boards)
        # So it's not functionally different except that it always takes the max time.
        
        mcu_ids_in_config = self.boards_config.keys()
        #self.status_receiver("mcu_ids_in_config",mcu_ids_in_config)

        if not (set(mcu_ids_in_config).issubset(set(mcu_ids_from_boards))):
            pass
            #self.status_receiver("missing board", set(mcu_ids_in_config).difference(set(mcu_ids_from_boards)))
            print("missing board", set(mcu_ids_in_config).difference(set(mcu_ids_from_boards)))
        else:
            # map mcu_ids to mcu_serial_device_paths
            #device_path_by_mcu_id = {board.mcu_id:board.serial_device_path for board in self.boards}
            device_path_by_mcu_id = {}
            for serial_id in self.boards:
                device_path_by_mcu_id[self.boards[serial_id].read_internal_mcu_id()] = serial_id

            # create motor instances
            for motor_name in self.motors_config:
                self.motors[motor_name] = Motor(
                    motor_name,
                    self.boards[device_path_by_mcu_id[self.motors_config[motor_name]["mcu_id"]]],
                    self.motors_config[motor_name]["channel"],
                    self.status_receiver
                )
            
            self.start()

    def get_device_id_list(self):
        matching_mcu_serial_device_paths = []
        for mcu_serial_device_path_pattern in self.mcu_serial_device_path_patterns:
            matching_mcu_serial_device_paths.extend(glob.glob(mcu_serial_device_path_pattern))
        return matching_mcu_serial_device_paths

    def match_mcu_id(self, mcu_serial_device_path):
        self.boards[mcu_serial_device_path] = Board(mcu_serial_device_path, self.add_to_queue)
        self.boards[mcu_serial_device_path].read_mcu_id(self._match_mcu_id)
        #self.match_mcu_id_temp_serial_device_path = mcu_serial_device_path

    def _match_mcu_id(self, mcu_serial_device_path, resp_str):
        self.boards[mcu_serial_device_path].add_mcu_id(resp_str)
        # handle exceptions:
        #   not a Roboteq device
        #   no response
        #   garbled response probably doesn't throw an exception

        # search config file for matching mcu_ids

        # if match found, create Motor instances, bind to Board instances
        # store reference to this mcu in Controllers
        
    def add_to_queue(self, mcu_serial_device_path, serial_command, resp_str, callback):
        self.queue.put((mcu_serial_device_path, serial_command, resp_str, callback))

    def run(self):
        while True:
            mcu_serial_device_path, serial_command, resp_str, callback = self.queue.get(True)
            try:
                callback(mcu_serial_device_path, serial_command, resp_str)
            except TypeError: #if callback == None
                pass
