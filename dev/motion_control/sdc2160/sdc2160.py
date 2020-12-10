#!/usr/bin/python3

import glob
import queue
import serial
import time
import threading


class status_types():
    DETECTED = "DETECTED"
    TESTED = "TESTED"
    READY = "READY"
    STOPPED = "STOPPED"





class Board(threading.Thread):
    def __init__(
            self, 
            serial_device_path, 
            controller_ref, 
            add_to_controller_queue,
            boards_config):
        threading.Thread.__init__(self)
        self.serial_device_path = serial_device_path
        self.controller_ref = controller_ref
        self.add_to_controller_queue = add_to_controller_queue
        self.boards_config = boards_config
        self.mcu_id = ""
        self.board_name = ""
        self.queue = queue.Queue()
        self.serial = serial.Serial(
            port=self.serial_device_path,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
        )
        self.states = {
            "B":None,
            "BKD":None,
            "BRUN":None,
            "CPRI":None,
            "ECHOF":None,
            "EE":None,
            "FF":None,
            "LK":None,
            "MXMD":None,
            "OVH":None,
            "OVL":None,
            "PWMF":None,
            "RSBR":None,
            "RWD":None,
            "THLD":None,
            "UID":None,
            "UVL":None,
            "V":None,
            "VAR":None,
        }

        time.sleep(1) # give serial a moment
        self.start()

    ##############################################
    #    MOTORS CONFIG                           #
    ##############################################
    def set_mixed_mode(self, mode):
        """
        Selects the mixed mode operation. It is applicable to dual channel controllers and serves
        to operate the two channels in mixed mode for tank-like steering. There are 3 possible
        values for this parameter for selecting separate or one of the two possible mixed mode
        algorithms. Details of each mixed mode is described in manual

        mode =
            0: Separate
            1: Mode 1
            2: Mode 2
        """
        serial_command = "^MXMD {}".format(mode)
        self.add_to_queue(serial_command)

    def get_mixed_mode(self, force_update = False):
        if self.states["MXMD"] is None or force_update:
            event = threading.Event()
            serial_command = "~MXMD"
            self.add_to_queue(serial_command, event, self._store_mixed_mode_)
            event.wait()
        return self.states["MXMD"]

    def _store_mixed_mode_(self, values_str, event):
        self.states["MXMD"] = values_str
        event.set()

    def set_pwm_frequency(self,kilohertz):
        """
        This parameter sets the PWM frequency of the switching output stage. It can be set from
        1 kHz to 20 kHz. The frequency is entered as kHz value multiplied by 10 (e.g. 185 = 18.5
        kHz). Beware that a too low frequency will create audible noise and would result in lower
        performance operation.
        """
        serial_command = "^PWMF {}".format(kilohertz)
        self.add_to_queue(serial_command)

    def get_pwm_frequency(self, force_update = False):
        if self.states["PWMF"] is None or force_update:
            event = threading.Event()
            serial_command = "~PWMF"
            self.add_to_queue(serial_command, event, self._store_pwm_frequency_)
            event.wait()
        return self.states["PWMF"]

    def _store_pwm_frequency_(self, values_str, event):
        self.states["PWMF"] = values_str
        event.set()

    ##############################################
    #    SAFETY                                  #
    ##############################################

    def get_runtime_fault_flags(self, force_update = False):
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
        if self.states["FF"] is None or force_update:
            event = threading.Event()
            serial_command = "?FF"
            self.add_to_queue(serial_command, event, self._store_runtime_fault_flags_)
            event.wait()
        return self.states["FF"]

    def _store_runtime_fault_flags_(self, values_str, event):
        values_int = int(values_str)
        self.states["FF"] = {
            "overheat":self._get_bit_(values_int, 0),
            "overvoltage":self._get_bit_(values_int, 1),
            "undervoltage":self._get_bit_(values_int, 2),
            "short_circuit":self._get_bit_(values_int, 3),
            "emergency_stop":self._get_bit_(values_int, 4),
            "brushless_sensor_fault":self._get_bit_(values_int, 5),
            "MOSFET_failure":self._get_bit_(values_int, 6),
            "default_configuration_loaded_at_startup":self._get_bit_(values_int, 7),
        }
        event.set()

    def get_volts(self, force_update = False):
        """
        Reports the voltages measured inside the controller at three locations: the main battery
        voltage, the internal voltage at the motor driver stage, and the voltage that is available on
        the 5V output on the DSUB 15 or 25 front connector. For safe operation, the driver stage
        voltage must be above 12V. The 5V output will typically show the controllerâ€TMs internal
        regulated 5V minus the drop of a diode that is used for protection and will be in the 4.7V
        range. The battery voltage is monitored for detecting the undervoltage or overvoltage con-
        ditions.
        """
        if self.states["V"] is None or force_update:
            event = threading.Event()
            serial_command = "?V"
            self.add_to_queue(serial_command, event, self._store_volts_)
            event.wait()
        return self.states["V"]

    def _store_volts_(self, values_str, event):
        self.states["V"] = values_str
        event.set()


    def emergency_stop(self):
        serial_command = "!EX"
        self.add_to_queue(serial_command)

    def emergency_stop_release(self):
        serial_command = "!MG"
        self.add_to_queue(serial_command)

    def set_serial_data_watchdog(self, miliseconds):
        serial_command = "^RWD {}".format(miliseconds)
        self.add_to_queue(serial_command)

    def get_serial_data_watchdog(self, force_update = False):
        if self.states["RWD"] is None or force_update:
            event = threading.Event()
            serial_command = "~RWD"
            self.add_to_queue(serial_command, event, self._store_serial_data_watchdog_)
            event.wait()
        return self.states["RWD"]

    def _store_serial_data_watchdog_(self, values_str, event):
        self.states["RWD"] = values_str
        event.set()

    def set_overvoltage_hysteresis(self,volts):
        """
        This voltage gets subtracted to the overvoltage limit to set the voltage at which the over-
        voltage condition will be cleared. For instance, if the overvoltage limit is set to 500 (50.0)
        and the hysteresis is set to 50 (5.0V), the MOSFETs will turn off when the voltage reach-
        es 50V and will remain off until the voltage drops under 45V
        """
        serial_command = "^OVH {}".format(volts*10)
        self.add_to_queue(serial_command)


    def get_overvoltage_hysteresis(self, force_update = False):
        if self.states["OVH"] is None or force_update:
            event = threading.Event()
            serial_command = "~OVH"
            self.add_to_queue(serial_command, event, self._store_overvoltage_hysteresis_)
            event.wait()
        return self.states["OVH"]

    def _store_overvoltage_hysteresis_(self, values_str, event):
        self.states["OVH"] = values_str
        event.set()
       
    def set_overvoltage_cutoff_threhold(self,volts):
        """
        Sets the voltage level at which the controller must turn off its power stage and signal an
        Overvoltage condition. Value is in volts multiplied by 10 (e.g. 450 = 45.0V) . The power
        stage will turn back on when voltage dips below the Overvoltage Clearing threshold that
        is set with the the OVH configuration command.

        Argument 1: Voltage
            Type: Unsigned 16-bit
            Min: 100 = 10.0V
            Max: See Product Datasheet
            Default: See Product Datasheet
        """
        serial_command = "^OVL {}".format(volts*10)
        self.add_to_queue(serial_command)

    def get_overvoltage_cutoff_threhold(self, force_update = False):
        if self.states["OVL"] is None or force_update:
            event = threading.Event()
            serial_command = "~OVL"
            self.add_to_queue(serial_command, event, self._store_overvoltage_cutoff_threhold_)
            event.wait()
        return self.states["OVL"]

    def _store_overvoltage_cutoff_threhold_(self, values_str, event):
        self.states["OVL"] = values_str
        event.set()


    def set_short_circuit_detection_threshold(self, option):
        """
        This configuration parameter sets the threshold level for the short circuit detection. There
        are 4 sensitivity levels from 0 to 3.

        option =
            0: Very high sensitivity
            1: Medium sensitivity
            2: Low sensitivity
            3: Short circuit protection disabled
        """
        serial_command = "^THLD {}".format(option)
        self.add_to_queue(serial_command)

    def get_short_circuit_detection_threshold(self, force_update = False):
        if self.states["THLD"] is None or force_update:
            event = threading.Event()
            serial_command = "~THLD"
            self.add_to_queue(serial_command, event, self._store_short_circuit_detection_threshold_)
            event.wait()
        return self.states["THLD"]

    def _store_short_circuit_detection_threshold_(self, values_str, event):
        self.states["THLD"] = values_str
        event.set()

    def set_undervoltage_limit(self,volts):
        """
        Sets the voltage below which the controller will turn off its power stage. The voltage is
        entered as a desired voltage value multiplied by 10. Undervoltage condition is cleared as
        soon as voltage rises above the limit.
        """
        serial_command = "^UVL {}".format(volts*10)
        self.add_to_queue(serial_command)

    def get_undervoltage_limit(self, force_update = False):
        if self.states["UVL"] is None or force_update:
            event = threading.Event()
            serial_command = "~UVL"
            self.add_to_queue(serial_command, event, self._store_undervoltage_limit_)
            event.wait()
        return self.states["UVL"]

    def _store_undervoltage_limit_(self, values_str, event):
        self.states["UVL"] = values_str
        event.set()

    def set_brake_activation_delay(self,miliseconds):
        """
        Set the delay in miliseconds from the time a motor stops and the time an output connect-
        ed to a brake solenoid will be released. Applies to any Digital Ouput(s) that is configured
        as motor brake. Delay value applies to all motors in multi-channel products.
        """
        serial_command = "^BKD {}".format(miliseconds)
        self.add_to_queue(serial_command)

    def get_brake_activation_delay(self, force_update = False):
        if self.states["BKD"] is None or force_update:
            event = threading.Event()
            serial_command = "~BKD"
            self.add_to_queue(serial_command, event, self._store_brake_activation_delay_)
            event.wait()
        return self.states["BKD"]

    def _store_brake_activation_delay_(self, values_str, event):
        self.states["BKD"] = values_str
        event.set()

    ##############################################
    #    SERIAL                                  #
    ##############################################
    def set_command_priorities(self, priority, source):
        """
        numbers indicating sources:
            0: Serial
            1: RC
            2: Analog (or Spektrum)
            3: None (or Alalog)
            4: None

        priority values start at 1

        example set_command_priorities("01,"0")
            set serial as first priority
        """
        serial_command = "^CPRI {} {}".format(priority, source)
        self.add_to_queue(serial_command)

    def get_command_priorities(self, force_update = False):
        if self.states["CPRI"] is None or force_update:
            event = threading.Event()
            serial_command = "~CPRI"
            self.add_to_queue(serial_command, event, self._store_command_priorities_)
            event.wait()
        return self.states["CPRI"]

    def _store_command_priorities_(self, values_str, event):
        self.states["CPRI"] = values_str
        event.set()

    def set_serial_echo(self, enable_disable):
        """
        enable_disable: :
            0: Echo is enabled
            1: Echo is disabled
        """
        serial_command = "^ECHOF {}".format(enable_disable)
        self.add_to_queue(serial_command)

    def get_serial_echo(self, force_update = False):
        if self.states["ECHOF"] is None or force_update:
            event = threading.Event()
            serial_command = "~ECHOF"
            self.add_to_queue(serial_command, event, self._store_serial_echo_)
            event.wait()
        return self.states["ECHOF"]

    def _store_serial_echo_(self, values_str, event):
        self.states["ECHOF"] = values_str
        event.set()

    def set_rs232_bit_rate(self, bit_rate_code):
        """
        bit_rate_code =
            0: 115200
            1: 57600
            2: 38400
            3:19200
            4: 9600
            5: 115200 + Inverted RS232
            6: 57600 + Inverted RS232
            7: 38400 + Inverted RS232
            8: 19200 + Inverted RS232
            9: 9600 + Inverted RS232
        """
        serial_command = "^RSBR {}".format(bit_rate_code)
        self.add_to_queue(serial_command)

    def get_rs232_bit_rate(self, force_update = False):
        if self.states["RSBR"] is None or force_update:
            event = threading.Event()
            serial_command = "~RSBR"
            self.add_to_queue(serial_command, event, self._store_rs232_bit_rate_)
            event.wait()
        return self.states["RSBR"]

    def _store_rs232_bit_rate_(self, values_str, event):
        self.states["RSBR"] = values_str
        event.set()


    ##############################################
    #    MEMORY                                  #
    ##############################################

    def get_mcu_id(self, force_update = False):
        if self.states["UID"] is None or force_update:
            event = threading.Event()
            serial_command = "?UID 2"
            self.add_to_queue(serial_command, event, self._store_mcu_id_)
            event.wait()
        return self.states["UID"]

    def _store_mcu_id_(self, values_str, event):
        self.states["UID"] = values_str
        self.mcu_id = values_str
        event.set()

    def set_user_boolean_variable(self, position, value):
        serial_command = "!B {} {}".format(position, value)
        self.add_to_queue(serial_command)

    def get_user_boolean_value(self, position, force_update = False):
        if self.states["B"] is None or force_update:
            event = threading.Event()
            serial_command = "?B"
            self.add_to_queue(serial_command, event, self._store_user_boolean_value_)
            event.wait()
        return self.states["B"]

    def _store_user_boolean_value_(self, values_str, event):
        self.states["B"] = values_str
        event.set()

    def set_user_variable(self, position, value):
        serial_command = "!VAR {} {}".format(position, value)
        self.add_to_queue(serial_command)

    def get_user_variable(self, position, force_update = False):
        if self.states["VAR"] is None or force_update:
            event = threading.Event()
            serial_command = "?VAR"
            self.add_to_queue(serial_command, event, self._store_user_variable_)
            event.wait()
        return self.states["VAR"]

    def _store_user_variable_(self, values_str, event):
        self.states["VAR"] = values_str
        event.set()

    def set_user_data_in_ram(self, address, data):
        """
        this must be followed by save_configuration_in_eeprom()
        The %EESAV Maintenance Command, or !EES
        Real Time Command must be used to copy the RAM array to Flash. The Flash is copied to
        RAM every time the device powers up.
        """
        serial_command = "^EE {} {}".format(address, data)
        self.add_to_queue(serial_command)

    def get_user_data_in_ram(self, force_update = False):
        if self.states["EE"] is None or force_update:
            event = threading.Event()
            serial_command = "~EE"
            self.add_to_queue(serial_command, event, self._store_user_data_in_ram_)
            event.wait()
        return self.states["EE"]

    def _store_user_data_in_ram_(self, values_str, event):
        self.states["EE"] = values_str
        event.set()


    def save_configuration_in_eeprom(self):
        serial_command = "%EESAV"
        #serial_command = "!EES"
        self.add_to_queue(serial_command)

    def get_lock_status(self, force_update = False):
        """
        Returns the status of the lock flag. If the configuration is locked, then it will not be possi-
        ble to read any configuration parameters until the lock is removed or until the parameters
        are reset to factory default. This feature is useful to protect the controller configuration
        from being copied by unauthorized people
        """
        if self.states["LK"] is None or force_update:
            event = threading.Event()
            serial_command = "?LK"
            self.add_to_queue(serial_command, event, self._store_lock_status_)
            event.wait()
        return self.states["LK"]

    def _store_lock_status_(self, values_str, event):
        self.states["LK"] = values_str
        event.set()

    ##############################################
    #    SCRIPTS                                 #
    ##############################################
    def set_script_auto_start(self, enable=0):
        """
        enable=
        0: Disabled
        1: Enabled after 2 seconds
        2: Enabled immediately
        """
        serial_command = "^BRUN {}".format(enable)
        self.add_to_queue(serial_command)

    def get_script_auto_start(self, force_update = False):
        if self.states["BRUN"] is None or force_update:
            event = threading.Event()
            serial_command = "~BRUN"
            self.add_to_queue(serial_command, event, self._store_script_auto_start_)
            event.wait()
        return self.states["BRUN"]

    def _store_script_auto_start_(self, values_str, event):
        self.states["BRUN"] = values_str
        event.set()

    def run_script(self):
        serial_command = "!R"
        self.add_to_queue(serial_command)


    ##############################################
    #    CLASS INTERNALS                         #
    ##############################################

    def _apply_settings_(self):
        config = self.boards_config[self.board_name]
        for setting in config:
            print("setting", setting)
            if setting == "serial_data_watchdog":
                self.set_serial_data_watchdog(config[setting])
            elif setting == "serial_echo":
                self.set_serial_echo(config[setting])

    def _get_bit_(self, number, place):
        return (number & (1 << place)) >> place

    def set_name(self, board_name):
        self.board_name = board_name

    def get_name(self):
        return self.board_name

    def read_internal_mcu_id(self):
        return self.mcu_id

    def add_mcu_id(self,mcu_id):
        self.mcu_id = mcu_id

    def add_to_queue(
            self, 
            serial_command, 
            event=None,
            callback=None):
        if event is not None:
            event.clear()
        self.queue.put((serial_command, event, callback))

    def _readSerial_(self):
        resp_char = " "
        resp_str = ""
        while ord(resp_char) != 13:
            resp_char = self.serial.read(1)
            resp_str += resp_char.decode('utf-8')
        resp_str = resp_str[:-1] # trim /r from end
        print("resp_str",resp_str)
        resp_l = resp_str.split('=')
        return resp_l

    def run(self):
        while True:
            serial_command, event, callback = self.queue.get(block=True, timeout=None)
            print('serial_command=',serial_command)
            self.serial.write(str.encode(serial_command +'\r'))
            resp = self._readSerial_()
            print(">>1",serial_command, resp)
            if len(resp)==1:
                if resp[0]=="+":
                    pass
                    # todo: do we need to pass affirmation?
                elif resp[0]=="-":
                    print("todo: response == '-' pass message of failure")
                else:# this is a command echo string.  now fetch command response
                    resp = self._readSerial_()
                    print(">>2",serial_command, resp)
                    if len(resp)!=2:
                        if resp == ['-']:
                            print("todo: response == '-' pass message of failure")
                    else:
                        if callback is not None:
                            callback(resp[1], event)













class Main(threading.Thread):
    def __init__(
            self,
            boards_config,
            motor_config,
            message_receiver,
            status_receiver, 
            exception_receiver,
            tb, #passed in to let module handle its own details
            mcu_serial_device_path_patterns=['/dev/serial/by-id/usb-FTDI*','/dev/serial/by-id/usb-Roboteq*']
        ):

        print(0)
        threading.Thread.__init__(self)
        self.boards_config = boards_config
        self.motor_config = motor_config
        self.message_receiver = message_receiver
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.tb = tb
        self.queue = queue.Queue()
        self.start()
        self.mcu_serial_device_path_patterns = mcu_serial_device_path_patterns
        print(1)
        self.mcu_serial_device_paths = self.get_device_id_list()
        print(2, self.mcu_serial_device_paths)
        
        for mcu_serial_device_path in self.mcu_serial_device_paths:
            print(3, mcu_serial_device_path)
            board = Board(
                mcu_serial_device_path, 
                self, 
                self.add_to_queue,
                self.boards_config)
            board.set_serial_echo(1)
            mcu_id = board.get_mcu_id(True)
            for name, val in self.boards_config.items():
                if val["mcu_id"] == mcu_id:
                    self.boards[name] = board
                    self.boards[name].set_name(name)
                    self.boards[name]._apply_settings_()
                    break

    def get_device_id_list(self):
        matching_mcu_serial_device_paths = []
        for mcu_serial_device_path_pattern in self.mcu_serial_device_path_patterns:
            matching_mcu_serial_device_paths.extend(glob.glob(mcu_serial_device_path_pattern))
        return matching_mcu_serial_device_paths
        


    def add_to_queue(self, command, params={}):
        self.queue.put((command, params))



    def run(self):
        pass













"""
    def speed(self,):

    def speed_phase(self,):

    def relative_position(self,):

    def absolute_position(self,):

    def torque(self,):

    def coast(self,):

    def home(self,):

    def oscillate(self,):

    def config(self,):
        
    def query(self,):
"""