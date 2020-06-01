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
    def __init__(self,path, controller_ref, add_to_controller_queue):
        threading.Thread.__init__(self)
        self.serial_device_path = path
        self.controller_ref = controller_ref
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
        time.sleep(0.5) # give serial a moment
        self.start()
        self.read_mcu_id()

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

    def read_mixed_mode(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_mixed_mode", response)
        else:
            serial_command = "~MXMD"
            self.add_to_queue(serial_command, self.read_mixed_mode)


    def set_pwm_frequency(self,kilohertz):
        """
        This parameter sets the PWM frequency of the switching output stage. It can be set from
        1 kHz to 20 kHz. The frequency is entered as kHz value multiplied by 10 (e.g. 185 = 18.5
        kHz). Beware that a too low frequency will create audible noise and would result in lower
        performance operation.
        """
        serial_command = "^PWMF {}".format(kilohertz)
        self.add_to_queue(serial_command)

    def read_pwm_frequency(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_pwm_frequency", response)
        else:
            serial_command = "~PWMF"
            self.add_to_queue(serial_command, self.read_pwm_frequency)

    ##############################################
    #    SAFETY                                  #
    ##############################################
    def read_volts(self, response=None):
        """
        Reports the voltages measured inside the controller at three locations: the main battery
        voltage, the internal voltage at the motor driver stage, and the voltage that is available on
        the 5V output on the DSUB 15 or 25 front connector. For safe operation, the driver stage
        voltage must be above 12V. The 5V output will typically show the controllerâ€TMs internal
        regulated 5V minus the drop of a diode that is used for protection and will be in the 4.7V
        range. The battery voltage is monitored for detecting the undervoltage or overvoltage con-
        ditions.
        """
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_volts", response)
        else:
            serial_command = "?V"
            self.add_to_queue(serial_command, self.read_volts)

    def emergency_stop(self):
        serial_command = "!EX"
        self.add_to_queue(serial_command)

    def emergency_stop_release(self):
        serial_command = "!MG"
        self.add_to_queue(serial_command)

    def set_serial_data_watchdog(self, miliseconds):
        serial_command = "^RWD {}".format(miliseconds)
        self.add_to_queue(serial_command)

    def read_serial_data_watchdog(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_serial_data_watchdog", response)
        else:
            serial_command = "~RWD"
            self.add_to_queue(serial_command, self.read_serial_data_watchdog)
        
    def set_overvoltage_hysteresis(self,volts):
        """
        This voltage gets subtracted to the overvoltage limit to set the voltage at which the over-
        voltage condition will be cleared. For instance, if the overvoltage limit is set to 500 (50.0)
        and the hysteresis is set to 50 (5.0V), the MOSFETs will turn off when the voltage reach-
        es 50V and will remain off until the voltage drops under 45V
        """
        serial_command = "^OVH {}".format(volts*10)
        self.add_to_queue(serial_command)

    def read_overvoltage_hysteresis(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_overvoltage_hysteresis", response)
        else:
            serial_command = "~OVH"
            self.add_to_queue(serial_command, self.read_overvoltage_hysteresis)
        
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

    def read_overvoltage_cutoff_threhold(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_overvoltage_cutoff_threhold", response)
        else:
            serial_command = "~OVL"
            self.add_to_queue(serial_command, self.read_overvoltage_cutoff_threhold)

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

    def read_short_circuit_detection_threshold(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_short_circuit_detection_threshold", response)
        else:
            serial_command = "~THLD"
            self.add_to_queue(serial_command, self.read_short_circuit_detection_threshold)

    def set_undervoltage_limit(self,volts):
        """
        Sets the voltage below which the controller will turn off its power stage. The voltage is
        entered as a desired voltage value multiplied by 10. Undervoltage condition is cleared as
        soon as voltage rises above the limit.
        """
        serial_command = "^UVL {}".format(volts*10)
        self.add_to_queue(serial_command)

    def read_undervoltage_limit(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_undervoltage_limit", response)
        else:
            serial_command = "~UVL"
            self.add_to_queue(serial_command, self.read_undervoltage_limit)

    def set_brake_activation_delay(self,miliseconds):
        """
        Set the delay in miliseconds from the time a motor stops and the time an output connect-
        ed to a brake solenoid will be released. Applies to any Digital Ouput(s) that is configured
        as motor brake. Delay value applies to all motors in multi-channel products.
        """
        serial_command = "^BKD {}".format(miliseconds)
        self.add_to_queue(serial_command)

    def read_brake_activation_delay(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_brake_activation_delay", response)
        else:
            serial_command = "~BKD"
            self.add_to_queue(serial_command, self.read_brake_activation_delay)

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

    def read_command_priorities(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_command_priorities", response)
        else:
            serial_command = "~CPRI"
            self.add_to_queue(serial_command)

    def set_serial_echo(self, enable_disable):
        """
        enable_disable: :
            0: Echo is enabled
            1: Echo is disabled
        """
        serial_command = "^ECHOF {}".format(enable_disable)
        self.add_to_queue(serial_command)

    def read_serial_echo(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_serial_echo", response)
        else:
            serial_command = "~ECHOF"
            self.add_to_queue(serial_command, self.read_serial_echo)

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

    def read_rs232_bit_rate(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_rs232_bit_rate", response)
        else:
            serial_command = "~RSBR"
            self.add_to_queue(serial_command, self.read_rs232_bit_rate)

    ##############################################
    #    MEMORY                                  #
    ##############################################
    def read_mcu_id(self, response=None):
        if response:
            self.add_mcu_id(response)
            self.controller_ref.match_boards_to_config(self.serial_device_path, response)
            #self.add_to_controller_queue(self.serial_device_path, None, "read_mcu_id", response)
        else:
            serial_command = "?UID"
            self.add_to_queue(serial_command, self.read_mcu_id)

    def set_user_boolean_variable(self, position, value):
        serial_command = "!B {} {}".format(position, value)
        self.add_to_queue(serial_command)

    def read_user_boolean_value(self, position):
        serial_command = "?B {}".format(position)
        self.add_to_queue(serial_command, self._read_user_boolean_value_)

    def _read_user_boolean_value_(self, response):
        self.add_to_controller_queue(self.serial_device_path, None, "read_user_boolean_value", response)

    def set_user_variable(self, position, value):
        serial_command = "!VAR {} {}".format(position, value)
        self.add_to_queue(serial_command)

    def read_user_variable(self, position):
        serial_command = "?VAR {}".format(position)
        self.add_to_queue(serial_command, self._read_user_variable_)

    def _read_user_variable_(self, response):
        self.add_to_controller_queue(self.serial_device_path, None, "read_user_variable", response)

    def set_user_data_in_ram(self, address, data):
        """
        this must be followed by save_configuration_in_eeprom()
        The %EESAV Maintenance Command, or !EES
        Real Time Command must be used to copy the RAM array to Flash. The Flash is copied to
        RAM every time the device powers up.
        """
        serial_command = "^EE {} {}".format(address, data)
        self.add_to_queue(serial_command)

    def read_user_data_in_ram(self, address):
        serial_command = "~EE {}".format(address)
        self.add_to_queue(serial_command)

    def save_configuration_in_eeprom(self):
        serial_command = "%EESAV"
        #serial_command = "!EES"
        self.add_to_queue(serial_command)

    def read_lock_status(self):
        """
        Returns the status of the lock flag. If the configuration is locked, then it will not be possi-
        ble to read any configuration parameters until the lock is removed or until the parameters
        are reset to factory default. This feature is useful to protect the controller configuration
        from being copied by unauthorized people
        """
        serial_command = "?LK"
        self.add_to_queue(serial_command)

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

    def read_script_auto_start(self, response=None):
        if response:
            self.add_to_controller_queue(self.serial_device_path, None, "read_script_auto_start", response)
        else:
            serial_command = "~BRUN"
            self.add_to_queue(serial_command, self.read_script_auto_start)

    def run_script(self):
        serial_command = "!R"
        self.add_to_queue(serial_command)

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
        #print(self.serial_device_path, "resp_str",resp_str)
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
            print("echo_str=", echo_str)
            resp_str = self._readSerial()
            print("resp_str=", resp_str)
            #print("callback",callback)
            try:
                callback(resp_str)
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
    #    MOTOR CONFIG                            #
    ##############################################
    def set_motor_acceleration_rate(self, rate):
        """
        Set the rate of speed change during acceleration for a motor channel. This command is
        identical to the AC realtime command. Acceleration value is in 0.1*RPM per sec-
        ond. When using controllers fitted with encoder, the speed and acceleration value
        are actual RPMs. Brushless motor controllers use the hall sensor for measuring actual
        speed and acceleration will also be in actual RPM/s. When using the controller without
        speed sensor, the acceleration value is relative to the Max RPM configuration parameter,
        which itself is a user-provide number for the speed normally expected speed at full power.
        Assuming that the Max RPM parameter is set to 1000, and acceleration value of 10000
        means that the motor will go from 0 to full speed in exactly 1 second, regardless of the
        actual motor speed.

        rate::
            Type: Signed 32-bit
            Min: 0
            Max: 500000
            Default: 10000 = 1000.0 RPM/s
        """
        serial_command = "^MAC {} {}".format(self.channel, rate)
        self.board.add_to_queue(serial_command)

    def read_motor_acceleration_rate(self):
        serial_command = "~MAC {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_motor_deceleration_rate(self, rate):
        """
        Set the rate of speed change during deceleration for a motor channel. This command is
        identical to the DC realtime command. Acceleration value is in 0.1*RPM per sec-
        ond. When using controllers fitted with encoder, the speed and deceleration value
        are actual RPMs. Brushless motor controllers use the hall sensor for measuring actual
        speed and acceleration will also be in actual RPM/s. When using the controller without
        speed sensor, the deceleration value is relative to the Max RPM configuration parameter,
        which itself is a user-provide number for the speed normally expected speed at full power.
        Assuming that the Max RPM parameter is set to 1000, and deceleration value of 10000
        means that the motor will go from full speed to 0 1 second, regardless of the actual motor
        speed.

        rate::
            Type: Signed 32-bit
            Min: 0
            Max: 500000
            Default: 10000 = 1000.0 RPM/s
        """
        serial_command = "^MDEC {} {}".format(self.channel, rate)
        self.board.add_to_queue(serial_command)

    def read_motor_deceleration_rate(self):
        serial_command = "~MDEC {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_operating_mode(self, mode):
        """
        This parameter lets you select the operating mode for that channel. See manual for de-
        scription of each mode

        nn =
            0: Open-loop
            1: Closed-loop speed
            2: Closed-loop position relative
            3: Closed-loop count position
            4: Closed-loop position tracking
            5: Torque
            6: Closed-loop speed position
        """
        serial_command = "^MMOD {} {}".format(self.channel, mode)
        self.board.add_to_queue(serial_command)

    def read_operating_mode(self):
        serial_command = "~MMOD {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_default_velocity_in_position_mode(self, velocity):
        """
        This parameter is the default speed at which the motor moves while in position mode.
        Values are in RPMs. To change velocity while the controller is in operation, use the !S run-
        time command.

        velocity:
            Type: Signed 32-bit
            Min: 0
            Default: 1000 RPM
            Max: 30000
        """
        serial_command = "^MVEL {} {}".format(self.channel, velocity)
        self.board.add_to_queue(serial_command)

    def read_default_velocity_in_position_mode(self):
        serial_command = "~MVEL {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_max_power_forward(self, max_power):
        """
        This parameter lets you select the scaling factor for the PWM output, in the forward direc-
        tion, as a percentage value. This feature is used to connect motors with voltage rating that
        is less than the battery voltage. For example, using a factor of 50% it is possible to con-
        nect a 12V motor onto a 24V system, in which case the motor will never see more than
        12V at its input even when the maximum power is applied.

        max_power:
            Type: Unsigned 8-bit
            Min: 25
            Default: 100%
        """
        serial_command = "^MXPF {} {}".format(self.channel, max_power)
        self.board.add_to_queue(serial_command)

    def read_max_power_forward(self):
        serial_command = "~MXPF {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_max_power_reverse(self, max_power):
        """
        This parameter lets you select the scaling factor for the PWM output, in the reverse direc-
        tion, as a percentage value. This feature is used to connect motors with voltage rating that
        is less than the battery voltage. For example, using a factor of 50% it is possible to con-
        nect a 12V motor onto a 24V system, in which case the motor will never see more than
        12V at its input even when the maximum power is applied.

        max_power:
            Type: Unsigned 8-bit
            Min: 25
            Default: 100%
        """
        serial_command = "^MXPR {} {}".format(self.channel, max_power)
        self.board.add_to_queue(serial_command)

    def read_max_power_reverse(self):
        serial_command = "~MXPR {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_max_rpm(self, max_rpm):
        """
        Commands sent via analog, pulse or the !G command only range between -1000 to
        +1000. The Max RPM parameter lets you select which actual speed, in RPM, will be con-
        sidered the speed to reach when a +1000 command is sent. In open loop, this parameter
        is used together with the acceleration and deceleration settings in order to figure the
        ramping time from 0 to full power.

        max_rpm
            Type: Unsigned 16-bit
            Min: 10
            Default: 1000 RPM
        """
        serial_command = "^MXRPM {} {}".format(self.channel, max_rpm)
        self.board.add_to_queue(serial_command)

    def read_max_rpm(self):
        serial_command = "~MXRPM {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    ##############################################
    #    MOTOR RUNTIME                           #
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

    def go_to_absolute_position(self, position):
        """Description:
        This command is used in the Position Count mode to make the motor move to a specified
        encoder or hall count value.
        Syntax Serial:
        !P [cc] nn
        """
        serial_command = "!P {} {}".format(self.channel, position)
        self.board.add_to_queue(serial_command)

    def go_to_relative_position(self, position):
        """
        Description:
        This command is used in the Position Count mode to make the motor move to an encoder
        count position that is relative to its current desired position.
        Syntax Serial:
        PR [cc] nn
                
        cc = Motor channel
        nn = Relative count position
        Example:
        !PR 1 10000 : while motor is stopped after power up and counter = 0, motor 1 will go to
        +10000
        !PR 2 10000 : while previous command was absolute goto position !P 2 5000, motor will
        go to +15000
        Note:
        Beware that counter will rollover at counter values +/-2’147’483’648.
        """
        serial_command = "!PR {} {}".format(self.channel, position)
        self.board.add_to_queue(serial_command)

    def set_motor_speed(self, speed): # -500,000 to 500,000
        """
        Description:
        In the Closed-Loop Speed mode, this command will cause the motor to spin at the de-
        sired RPM speed. In Closed-Loop Position modes, this commands determines the speed
        at which the motor will move from one position to the next. It will not actually start the
        motion.
        Syntax Serial:
        !S [cc] nn
        Where:
        cc = Motor channel
        nn = Speed value in RPM
        Example:
        !S 2500 : set motor 1 position velocity to 2500 RPM
        """
        serial_command = "!S {} {}".format(self.channel, speed)
        self.board.add_to_queue(serial_command)

    def set_acceleration(self, acceleration): # 0-50000. Acceleration value is in 0.1 * RPM per second.  
        if acceleration > 500000:
            acceleration = 500000
        if acceleration < 0:
            acceleration = 0
        serial_command = "!AC {} {}".format(self.channel, acceleration)
        self.board.add_to_queue(serial_command)

    def set_deceleration(self, deceleration): # 0-50000. Acceleration value is in 0.1 * RPM per second.  
        if deceleration > 500000:
            deceleration = 500000
        if deceleration < 0:
            deceleration = 0
        serial_command = "!DC {} {}".format(self.channel, deceleration)
        self.board.add_to_queue(serial_command)

    def read_motor_power_output_applied(self):
        """
        Reports the actual PWM level that is being applied to the motor at the power output
        stage. This value takes into account all the internal corrections and any limiting resulting
        from temperature or over current. A value of 1000 equals 100% PWM. The equivalent
        voltage at the motor wire is the battery voltage * PWM level.

        Reply:
        P=nn
        Type: Signed 16-bit
        Min: -1000
        Max: 1000
        """
        serial_command = "?P {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def read_motor_amps(self):
        """
        Measures and reports the motor Amps for all operating channels. Note that the current
        flowing through the motors is often higher than this flowing through the battery.
        """
        serial_command = "?A {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    ##############################################
    #    PID SETUP                               #
    ##############################################
    def set_pid_integral_cap(self, cap):
        """
        This parameter is the integral cap as a percentage. This parameter will limit maximum
        level of the Integral factor in the PID. It is particularly useful in position systems with long
        travel movement, and where the integral factor would otherwise become very large be-
        cause of the extended time the integral would allow to accumulate. This parameter can
        be used to dampen the effect of the integral parameter without reducing the gain. This
        parameter may adversely affect system performance in closed loop speed mode as the
        Integrator must be allowed to reach high values in order for good speed control.

        cap:
            Type: Unsigned 8-bit
            Min: 1
            Default: 100%
        """
        serial_command = "^ICAP {} {}".format(self.channel, cap)
        self.board.add_to_queue(serial_command)

    def read_pid_integrap_cap(self):
        serial_command = "~ICAP {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_pid_differential_gain(self, gain):
        """
        Sets the PID's Differential Gain for that channel. The value is set as the gain multiplied by
        10. This gain is used in all closed loop modes. In Torque mode, when sinusoidal mode is
        selected on brushless contontrollers, the FOC's PID is used instead the this parameter
        has no effect.

        gain:
            Type: Unsigned 8-bit
            Min: 0
            Default: 0

        Note:
        Do not use default values. As a starting point, se P=2, I=0, D=0 in position modes (includ-
        ing Speed Position mode). Use P=0, I=1, D=0 in closed loop speed mode and in torque
        mode. Perform full tuning after that.
        """
        serial_command = "^KD {} {}".format(self.channel, gain*10)
        self.board.add_to_queue(serial_command)

    def read_pid_differential_gain(self):
        serial_command = "~KD {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_pid_integral_gain(self, gain):
        """
        Sets the PID's Integral Gain for that channel. The value is set as the gain multiplied by 10.
        This gain is used in all closed loop modes. In Torque mode, when sinusoidal mode is se-
        lected on brushless controllers, the FOC's PID is used instead the this parameter has no
        effect.

        gain:
            Type: Unsigned 8-bit
            Min: 0
            Default: 20 = 2.0 Max: 255
        """
        serial_command = "^KI {} {}".format(self.channel, gain*10)
        self.board.add_to_queue(serial_command)

    def read_pid_integral_gain(self):
        serial_command = "~KI {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_pid_proportional_gain(self, gain):
        """
        Sets the PID's Proportional Gain for that channel. The value is set as the gain multiplied by
        10. This gain is used in all closed loop modes. In Torque mode, when sinusoidal mode is
        selected on brushless controllers, the FOC's PID is used instead the this parameter has
        no effect.

        gain:
            Type: Unsigned 8-bit
            Min: 0
            Default: 20 = 2.0 Max: 255
        """
        serial_command = "^KP {} {}".format(self.channel, gain*10)
        self.board.add_to_queue(serial_command)

    def read_pid_proportional_gain(self):
        serial_command = "~KP {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    ##############################################
    #    PID RUNTIME                             #
    ##############################################
    def read_expected_motor_position(self):
        """
        Reads the real-time value of the expected motor position in the position tracking closed
        loop mode and in speed position
        """
        serial_command = "?TR {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    ##############################################
    #    ENCODERS SETUP                          #
    ##############################################

    def set_encoder_counter(self, value):
        serial_command = "!C {} {}".format(self.channel, value)
        self.board.add_to_queue(serial_command)

    def set_sensor_type_select(self, encoder_or_other):
        """
        This parameter is used to select which feedback sensor will be used to measure speed
        or positions. On brushless motors system equipped with optical encoders, this parame-
        ter lets you select the encoder or the brushless sensors (ie. Hall, Sin/Cos, or SPI) as the
        source of speed or position feedback. Encoders provide higher precision capture and
        should be preferred whenever possible. The choice Other is also used to select pulse or
        analog feedback in some position modes,

        encoder_or_other =
            0: Other feedback
            1: Brushless sensor feedback (Hall, SPI, Sin/Cos)
        """
        serial_command = "^BLFB {} {}".format(self.channel, encoder_or_other)
        self.board.add_to_queue(serial_command)

    def read_sensor_type_select(self):
        serial_command = "~BLFB {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_encoder_usage(self, action):
        """
        This parameter defines what use the encoder is for. The encoder can be used to set com-
        mand or to provide feedback (speed or position feedback). The use of encoder as feedback
        devices is the most common. Embedded in the parameter is the motor to which the en-
        coder is associated.
        aa =
        0: Unused
        1: Command
        2: Feedback
        mm =
        mot1*16 + mot2*32 + mot3*48

        """
        serial_command = "^EMOD {} {}".format(self.channel, action + self.bit_offset)
        self.board.add_to_queue(serial_command)

    def read_encoder_usage(self):
        serial_command = "~EMOD {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_encoder_ppr_value(self, ppr):
        """
        This parameter will set the pulse per revolution of the encoder that is attached to the con-
        troller. The PPR is the number of pulses that is issued by the encoder when making a full
        turn. For each pulse there will be 4 counts which means that the total number of a count-
        er increments inside the controller will be 4x the PPR value. Make sure not to confuse the
        Pulse Per Revolution and the Count Per Revolution when setting up this parameter. Enter-
        ing a negative number will invert the counter and the measured speed polarity

        ppr:
            Type: Signed 16-bit
            Min: -32768
            Default: 100 Max: 32767
        """
        serial_command = "^EPPR {} {}".format(self.channel, ppr)
        self.board.add_to_queue(serial_command)

    def read_encoder_ppr_value(self):
        serial_command = "~EPPR {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    ##############################################
    #    ENCODERS RUNTIME                        #
    ##############################################
    def read_encoder_counter_absolute(self):
        """
        Returns the encoder value as an absolute number. The counter is 32-bit with a range of
        +/- 2147483648 counts.

        Type: Signed 32-bit
        Min: -2147M
        Max: 2147M
        """
        serial_command = "?C {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def read_feedback(self):
        """
        Reports the value of the feedback sensors that are associated to each of the channels in
        closed-loop modes. The feedback source can be Encoder, Analog or Pulse. Selecting the
        feedback source is done using the encoder, pulse or analog configuration parameters. This
        query is useful for verifying that the correct feedback source is used by the channel in the
        closed-loop mode and that its value is in range with expectations.
        """
        serial_command = "?F {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def read_encoder_counter_relative(self):
        """
        Returns the amount of counts that have been measured from the last time this query was
        made. Relative counter read is sometimes easier to work with, compared to full counter
        reading, as smaller numbers are usually returned.
        """
        serial_command = "~CR {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def read_encoder_speed_relative(self):
        """
        Returns the measured motor speed as a ratio of the Max RPM (MXRPM) configuration
        parameter. The result is a value of between 0 and +/1000. As an example, if the Max RPM
        is set at 3000 inside the encoder configuration parameter and the motor spins at 1500
        RPM, then the returned value to this query will be 500, which is 50% of the 3000 max.
        Note that if the motor spins faster than the Max RPM, the returned value will exceed
        1000. However, a larger value is ignored by the controller for its internal operation

        Reply:
            SR = nn Type: Signed 16-bit
            Min: -1000
            Max: 1000
        """
        serial_command = "?SR {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def read_encoder_motor_speed_in_rpm(self):
        """
        Reports the actual speed measured by the encoders as the actual RPM value. To report
        RPM accurately, the correct Pulses per Revolution (PPR) must be
        """
        serial_command = "?S {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def read_encoder_speed_relative(self):
        """
        Returns the measured motor speed as a ratio of the Max RPM (MXRPM) configuration
        parameter. The result is a value of between 0 and +/1000. As an example, if the Max RPM
        is set at 3000 inside the encoder configuration parameter and the motor spins at 1500
        RPM, then the returned value to this query will be 500, which is 50% of the 3000 max.
        Note that if the motor spins faster than the Max RPM, the returned value will exceed
        1000. However, a larger value is ignored by the controller for its internal operation

        Reply:
            SR = nn Type: Signed 16-bit
            Min: -1000
            Max: 1000
        """
        serial_command = "?SR {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    ##############################################
    #    SAFETY                                  #
    ##############################################
    def emergency_stop(self):
        serial_command = "!MS {}".format(self.channel)
        self.board.add_to_queue(serial_command)


    def read_config_flags(self):
        """
        Report the state of status flags used by the controller to indicate a number of internal
        conditions during normal operation. The response to this query is the single number for all
        status flags. The status of individual flags is read by converting this number to binary and
        look at various bits of that number


        f1 = Serial mode
        f2 = Pulse mode
        f3 = Analog mode
        f4 = Power stage off
        f5 = Stall detected
        f6 = At limit
        f7 = Unused
        f8 = MicroBasic script running

        FS = f1 + f2*2 + f3*4 + ... + fn*2^n-1
        """
        serial_command = "?FS {}".format(self.channel)
        self.board.add_to_queue(serial_command)


    def set_current_limit(self, amps):
        serial_command = "^ALIM {} {}".format(self.channel, amps * 10)
        self.board.add_to_queue(serial_command)

    def read_current_limit(self):
        serial_command = "~ALIM {}".format(self.channel)
        self.board.add_to_queue(serial_command)
  
    def set_current_limit_action(self, action):
        """
            action =
            0 : No action
            1: Safety stop
            2: Emergency stop
            3: Motor stop
            4: Forward limit switch
            5: Reverse limit switch
            6: Invert direction
            7: Run MicroBasic script
            8: Load counter with home value

            
            mm = mot1*16 + mot2*32 + mot3*48

        """
        serial_command = "^ATGA {} {}".format(self.channel, action + self.bit_offset)
        self.board.add_to_queue(serial_command)

    def read_current_limit_action(self):
        serial_command = "~ATGA {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_current_limit_min_period(self, milliseconds):
        """
        This parameter contains the time in milliseconds during which the Amps Trigger Level
        (ATRIG) must be exceeded before the Amps Trigger Action (ATGA) is called. This parame-
        ter is used to prevent Amps Trigger Actions to be taken in case of short duration spikes.
        """
        serial_command = "^ATGD {} {}".format(self.channel, mililseconds)
        self.board.add_to_queue(serial_command)

    def read_current_limit_min_period(self):
        """
        This parameter contains the time in milliseconds during which the Amps Trigger Level
        (ATRIG) must be exceeded before the Amps Trigger Action (ATGA) is called. This parame-
        ter is used to prevent Amps Trigger Actions to be taken in case of short duration spikes.
        """
        serial_command = "~ATGD {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_current_limit_amps(self, amps):
        """
        This parameter lets you select Amps threshold value that will trigger an action. This
        threshold must be set to be below the ALIM Amps limit. When that threshold is reached,
        then list of action can be selected using the ATGA parameter
        """
        serial_command = "^ATRIG {} {}".format(self.channel, amps*10)
        self.board.add_to_queue(serial_command)

    def read_current_limit_amps(self):
        serial_command = "~ATRIG {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_stall_detection(self, threshold):
        """
        Description:
        This parameter controls the stall detection of brushless motors and of brushed
        motors in closed loop speed mode. If no motion is sensed (i.e. counter remains un-
        changed) for a preset amount of time while the power applied is above a given
        threshold, a stall condition is detected and the power to the motor is cut until
        the command is returned to 0. This parameter allows three combination of time &
        power sensitivities. The setting also applies also when encoders are used in closed loop
        speed mode on brushed or brushless motors

        threshold =
            0: Disabled
            1: 250ms at 10% Power
            2: 500ms at 25% Power
            3: 1000ms at 50% Power
        """
        serial_command = "^BLSTD {} {}".format(self.channel, threshold)
        self.board.add_to_queue(serial_command)

    def read_stall_detection(self):
        serial_command = "~BLSTD {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_closed_loop_error_detection(self, threshold):
        """
        This parameter is used to detect large tracking errors due to mechanical or sensor failures,
        and shut down the motor in case of problem in closed loop speed or position system. The
        detection mechanism looks for the size of the tracking error and the duration the error is
        present. This parameter allows three combination of time & error level. This parameter
        is also used to limit the loop error when operating in Count Position, and Speed Position
        modes. When enabled, the desired position (tracking) will stop progressing when the loop
        error is greater than 50% the detection threshold while power output is already at 100%.

        threshold =
        0: Detection disabled
        1: 250ms at Error > 100
        2: 500ms at Error > 250
        3: 1000ms at Error > 500

        """
        serial_command = "^CLERD {} {}".format(self.channel, threshold)
        self.board.add_to_queue(serial_command)

    def read_closed_loop_error_detection(self):
        serial_command = "~CLERD {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_encoder_high_count_limit(self, limit):
        """
        Defines a maximum count value at which the controller will trigger an action when the
        counter goes above that number. This feature is useful for setting up 
        limit switches .This value, together with the Low Count Limit, are also used in the posi-
        tion mode to determine the travel range when commanding the controller with a relative
        position command. In this case, the High Limit Count is the desired position when a com-
        mand of 1000 is received.

            Type: Signed 32-bit
            Min: -2147M
            Default: +20000 Max: 2147M
        """
        serial_command = "^EHL {} {}".format(self.channel, limit)
        self.board.add_to_queue(serial_command)

    def read_encoder_high_count_limit(self):
        serial_command = "~EHL {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_encoder_high_limit_action(self, action):
        """
        This parameter lets you select what kind of action should be taken when the high limit
        count is reached on the encoder. The list of action is the same as in the DINA digital input
        action list Embedded in the parameter is the motor channel(s) to which the action should
        apply.

        action =
            0: No action
            1: Safety stop
            2: Emergency stop
            3: Motor stop
            4: Forward limit switch
            5: Reverse limit switch
            6: Invert direction
            7: Run MicroBasic script
            8: Load counter with home value
            mm = mot1*16 + mot2*32 + mot3*48
        """

        serial_command = "^EHLA {} {}".format(self.channel, action + self.bit_offset)
        self.board.add_to_queue(serial_command)

    def read_encoder_high_limit_action(self):
        serial_command = "~EHLA {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_encoder_low_count_limit(self, limit):
        """
            Defines a minimum count value at which the controller will trigger an action when the
            counter dips below that number. This feature is useful for setting up 
            limit switches.This value, together with the High Count Limit, are also used in the position
            mode to determine the travel range when commanding the controller with a relative posi-
            tion command. In this case, the Low Limit Count is the desired position when a command
            of -1000 is received.

            Type: Signed 32-bit
            Min: -2147M
            Default: -20000 Max: 2147M
        """
        serial_command = "^ELL {} {}".format(self.channel, limit)
        self.board.add_to_queue(serial_command)

    def read_encoder_low_count_limit(self):
        serial_command = "~ELL {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def set_encoder_low_limit_action(self, action):
        """
        This parameter lets you select what kind of action should be taken when the low limit
        count is reached on the encoder. The list of action is the same as in the DINA digital input
        action list Embedded in the parameter is the motor channel(s) to which the action should
        apply.

        action =
            0: No action
            1: Safety stop
            2: Emergency stop
            3: Motor stop
            4: Forward limit switch
            5: Reverse limit switch
            6: Invert direction
            7: Run MicroBasic script
            8: Load counter with home value
            mm = mot1*16 + mot2*32 + mot3*48
        """
        serial_command = "^ELLA {} {}".format(self.channel, action + self.bit_offset)
        self.board.add_to_queue(serial_command)

    def read_encoder_low_limit_action(self):
        serial_command = "~ELLA {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def read_closed_loop_error(self):
        """
        In closed-loop modes, returns the difference between the desired speed or position and
        the measured feedback. This query can be used to detect when the motor has reached
        the desired speed or position. In open loop mode, this query returns 0.
        """
        serial_command = "?E {}".format(self.channel)
        self.board.add_to_queue(serial_command)

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

    def read_runtime_status_flags(self):
        """
        Report the runtime status of each motor. The response to that query is a single number
        which must be converted into binary in order to evaluate each of the individual status bits
        that compose it.

        flag meaning:
            f1 = Amps Limit currently active
            f2 = Motor stalled
            f3 = Loop Error detected
            f4 = Safety Stop active
            f5 = Forward Limit triggered
            f6 = Reverse Limit triggered
            f7 = Amps Trigger activated

            FM = f1 + f2*2 + f3*4 + ... + fn*2n-1
        """
        serial_command = "?FM {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    def read_temperature(self, response = None):
        """
        Reports the temperature at each of the Heatsink sides and on the internal MCU silicon
        chip. The reported value is in degrees C with a one degree resolution.

        Reply:
            T= cc
            Type: Signed 8-bit Min: -40 Max: 125
        """
        serial_command = "?T {}".format(self.channel)
        self.board.add_to_queue(serial_command)

    ##############################################
    #    CLASS INTERNALS                         #
    ##############################################

    def add_to_queue(self, serial_command, value, callback):
        self.queue.put((serial_command, value, callback))

    def run(self):
        while True:
            #try:
            serial_command, value, callback = self.queue.get(block=True) #, timeout=0.5)
            #except queue.Empty:
            #    self.read_encoder_counter_absolute()



















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
        self.start()
        # create board objects and read their mcu_ids
        for mcu_serial_device_path in self.mcu_serial_device_paths:
            self.boards[mcu_serial_device_path] = Board(mcu_serial_device_path, self, self.add_to_queue)

    def match_boards_to_config(self, mcu_serial_device_path, resp_str):
        # this method verifies that all mcu_ids listed in config can be matched with discovered boards.
        found = True
        mcu_ids_in_config = list(self.boards_config.keys())
        for board in self.boards.values():
            mcu_ids_in_config.remove(board.read_internal_mcu_id())
        if len(mcu_ids_in_config) == 0:
            self.create_motors()

    def create_motors(self):
        device_path_by_mcu_id = {}
        for serial_id in self.boards:
            device_path_by_mcu_id[self.boards[serial_id].read_internal_mcu_id()] = serial_id

        for motor_name in self.motors_config:
            self.motors[motor_name] = Motor(
                motor_name,
                self.boards[device_path_by_mcu_id[self.motors_config[motor_name]["mcu_id"]]],
                self.motors_config[motor_name]["channel"],
                self.status_receiver
            )

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
