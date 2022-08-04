"""
This wrapper is for individual SDCs, not multiples. 

usage:

import SDC
sdc = SDC(
    config=,
    fault_callback=,
    data_receiver=,
    status_receiver=, 
    exception_receiver=,
)
sdc.test_presence()
sdc.motor_1.set_speed()
sdc.motor_2.set_speed()

position, success = SDC2130.get_position()

to do:
make this work for version other than RCB100
unify the types of status messages

"""

#!/usr/bin/python

import glob
import os
import queue
import RPi.GPIO as GPIO 
import serial
import sys
import time
import threading

sample_config = {
    "brake_activation_delay": 250,
    "command_priorities": ["0", "1", "2", "4"],
    "lock_status": 0,
    "mixed_mode": 0,
    "overvoltage_cutoff_threhold": 30.0,
    "pwm_frequency": 160,
    "script_auto_start": 0,
    "serial_data_watchdog": 1000,
    "serial_echo": 0,
    "short_circuit_detection_threshold": 1,
    "undervoltage_limit": 50,
    "motor_1": {
        "closed_loop_error_detection": 0,
        "current_limit": 20.0,
        "current_limit_action": 0,
        "current_limit_amps": 75.0,
        "current_limit_min_period": 500,
        "default_velocity_in_position_mode": 50,
        "encoder_high_count_limit": 42000,
        "encoder_high_limit_action": 0,
        "encoder_low_count_limit": -42000,
        "encoder_low_limit_action": 0,
        "encoder_ppr_value": 512,
        "encoder_usage": 2,
        "max_power_forward": 100,
        "max_power_reverse": 100,
        "max_rpm": 1000,
        "motor_acceleration_rate": 10000,
        "motor_deceleration_rate": 10000,
        "operating_mode": 1,
        "pid_differential_gain": 1.0,
        "pid_integral_cap": 100,
        "pid_integral_gain": 2.0,
        "pid_proportional_gain": 1.0,
        "sensor_type_select": [0, 18],
        "stall_detection": 0,
    },
    "motor_2": {
        "closed_loop_error_detection": 0,
        "current_limit": 20.0,
        "current_limit_action": 0,
        "current_limit_amps": 75.0,
        "current_limit_min_period": 500,
        "default_velocity_in_position_mode": 50,
        "encoder_high_count_limit": 42000,
        "encoder_high_limit_action": 0,
        "encoder_low_count_limit": -42000,
        "encoder_low_limit_action": 0,
        "encoder_ppr_value": 512,
        "encoder_usage": 2,
        "max_power_forward": 100,
        "max_power_reverse": 100,
        "max_rpm": 1000,
        "motor_acceleration_rate": 10000,
        "motor_deceleration_rate": 10000,
        "operating_mode": 1,
        "pid_differential_gain": 1.0,
        "pid_integral_cap": 100,
        "pid_integral_gain": 2.0,
        "pid_proportional_gain": 1.0,
        "sensor_type_select": [0, 18],
        "stall_detection": 18,
    },
}


#@capture_exceptions.Class
class Status_Poller(threading.Thread):
    def __init__(
            self, 
            sdc,
            data_receiver, 
            status_receiver, 
            exception_receiver,
            period_s=0.1, 
            report_position=False,
        ):
        threading.Thread.__init__(self)
        self.sdc = sdc
        self.data_receiver = data_receiver
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.period_s = period_s
        self.report_position = report_position
        self.states = {
            "motor_1_duty_cycle":0,
            "motor_1_motor_amps":0,
            "motor_1_encoder_counter_absolute":0,
            "motor_1_encoder_motor_speed_in_rpm":0,
            "motor_1_closed_loop_error":0,
            "motor_1_temperature":0,
            "motor_1_amps_limit_activated":0,
            "motor_1_motor_stalled":0,
            "motor_1_loop_error_detected":0,
            "motor_1_safety_stop_active":0,
            "motor_1_forward_limit_triggered":0,
            "motor_1_reverse_limit_triggered":0,
            "motor_1_amps_trigger_activated":0,
            "motor_2_duty_cycle":0,
            "motor_2_motor_amps":0,
            "motor_2_encoder_counter_absolute":0,
            "motor_2_encoder_motor_speed_in_rpm":0,
            "motor_2_closed_loop_error":0,
            "motor_2_temperature":0,
            "motor_2_amps_limit_activated":0,
            "motor_2_motor_stalled":0,
            "motor_2_loop_error_detected":0,
            "motor_2_safety_stop_active":0,
            "motor_2_forward_limit_triggered":0,
            "motor_2_reverse_limit_triggered":0,
            "motor_2_amps_trigger_activated":0,
            "overheat":0,
            "overvoltage":0,
            "undervoltage":0,
            "short_circuit":0,
            "emergency_stop":0,
            "brushless_sensor_fault":0,
            "MOSFET_failure":0,
            "default_configuration_loaded_at_startup":0,
        }
        self.queue = queue.Queue()

    def run(self):
        while True:
            self.sdc.set_digital_out_bits(1) # this is just to keep the command watchdog alive

            """
            motor_1_duty_cycle = self.sdc.motor_1.get_duty_cycle()
            if motor_1_duty_cycle != self.states["motor_1_duty_cycle"]:
                #self.status_receiver("motor_1_duty_cycle",motor_1_duty_cycle)
                self.states["motor_1_duty_cycle"] = motor_1_duty_cycle
            motor_2_duty_cycle = self.sdc.motor_2.get_duty_cycle()
            if motor_2_duty_cycle != self.states["motor_2_duty_cycle"]:
                #self.status_receiver("motor_2_duty_cycle",motor_2_duty_cycle)
                self.states["motor_2_duty_cycle"] = motor_2_duty_cycle
            time.sleep(self.period_s)

            motor_1_motor_amps = self.sdc.motor_1.get_motor_amps()
            if motor_1_motor_amps != self.states["motor_1_motor_amps"]:
                #self.status_receiver("motor_1_motor_amps",motor_1_motor_amps)
                self.states["motor_1_motor_amps"] = motor_1_motor_amps
            motor_2_motor_amps = self.sdc.motor_2.get_motor_amps()
            if motor_2_motor_amps != self.states["motor_2_motor_amps"]:
                #self.status_receiver("motor_2_motor_amps",motor_2_motor_amps)
                self.states["motor_2_motor_amps"] = motor_2_motor_amps
            time.sleep(self.period_s)

            if self.report_position:
                motor_1_encoder_counter_absolute = self.sdc.motor_1.get_encoder_counter_absolute()
                if motor_1_encoder_counter_absolute != self.states["motor_1_encoder_counter_absolute"]:
                    #self.status_receiver("motor_1_encoder_counter_absolute",motor_1_encoder_counter_absolute)
                    self.states["motor_1_encoder_counter_absolute"] = motor_1_encoder_counter_absolute
                motor_2_encoder_counter_absolute = self.sdc.motor_2.get_encoder_counter_absolute()
                if motor_2_encoder_counter_absolute != self.states["motor_2_encoder_counter_absolute"]:
                    #self.status_receiver("motor_2_encoder_counter_absolute",motor_2_encoder_counter_absolute)
                    self.states["motor_2_encoder_counter_absolute"] = motor_2_encoder_counter_absolute
                time.sleep(self.period_s)

            motor_1_encoder_motor_speed_in_rpm = self.sdc.motor_1.get_encoder_motor_speed_in_rpm()
            if motor_1_encoder_motor_speed_in_rpm != self.states["motor_1_encoder_motor_speed_in_rpm"]:
                #self.status_receiver("motor_1_encoder_motor_speed_in_rpm",motor_1_encoder_motor_speed_in_rpm)
                self.states["motor_1_encoder_motor_speed_in_rpm"] = motor_1_encoder_motor_speed_in_rpm
            motor_2_encoder_motor_speed_in_rpm = self.sdc.motor_2.get_encoder_motor_speed_in_rpm()
            if motor_2_encoder_motor_speed_in_rpm != self.states["motor_2_encoder_motor_speed_in_rpm"]:
                #self.status_receiver("motor_2_encoder_motor_speed_in_rpm",motor_2_encoder_motor_speed_in_rpm)
                self.states["motor_2_encoder_motor_speed_in_rpm"] = motor_2_encoder_motor_speed_in_rpm
            time.sleep(self.period_s)
            motor_1_closed_loop_error = self.sdc.motor_1.get_closed_loop_error()
            if motor_1_closed_loop_error != self.states["motor_1_closed_loop_error"]:
                #self.status_receiver("motor_1_closed_loop_error",motor_1_closed_loop_error)
                self.states["motor_1_closed_loop_error"] = motor_1_closed_loop_error
            motor_2_closed_loop_error = self.sdc.motor_2.get_closed_loop_error()
            if motor_2_closed_loop_error != self.states["motor_2_closed_loop_error"]:
                #self.status_receiver("motor_2_closed_loop_error",motor_2_closed_loop_error)
                self.states["motor_2_closed_loop_error"] = motor_2_closed_loop_error
            time.sleep(self.period_s)
            motor_1_temperature = self.sdc.motor_1.get_temperature()
            if motor_1_temperature != self.states["motor_1_temperature"]:
                self.status_receiver("motor_1_temperature",motor_1_temperature)
                self.states["motor_1_temperature"] = motor_1_temperature
            motor_2_temperature = self.sdc.motor_2.get_temperature()
            if motor_2_temperature != self.states["motor_2_temperature"]:
                self.status_receiver("motor_2_temperature",motor_2_temperature)
                self.states["motor_2_temperature"] = motor_2_temperature
            time.sleep(self.period_s)
            runtime_status_flags = self.sdc.motor_1.get_runtime_status_flags()
            if runtime_status_flags["amps_limit_activated"] != self.states["motor_1_amps_limit_activated"]:
                self.status_receiver("motor_1_amps_limit_activated",runtime_status_flags["amps_limit_activated"])
                self.states["motor_1_amps_limit_activated"] = runtime_status_flags["amps_limit_activated"]
            if runtime_status_flags["motor_stalled"] != self.states["motor_1_motor_stalled"]:
                self.status_receiver("motor_1_motor_stalled",runtime_status_flags["motor_stalled"])
                self.states["motor_1_motor_stalled"] = runtime_status_flags["motor_stalled"]
            if runtime_status_flags["loop_error_detected"] != self.states["motor_1_loop_error_detected"]:
                self.status_receiver("motor_1_loop_error_detected",runtime_status_flags["loop_error_detected"])
                self.states["motor_1_loop_error_detected"] = runtime_status_flags["loop_error_detected"]
            if runtime_status_flags["safety_stop_active"] != self.states["motor_1_safety_stop_active"]:
                self.status_receiver("motor_1_safety_stop_active",runtime_status_flags["safety_stop_active"])
                self.states["motor_1_safety_stop_active"] = runtime_status_flags["safety_stop_active"]
            if runtime_status_flags["forward_limit_triggered"] != self.states["motor_1_forward_limit_triggered"]:
                self.status_receiver("motor_1_forward_limit_triggered",runtime_status_flags["forward_limit_triggered"])
                self.states["motor_1_forward_limit_triggered"] = runtime_status_flags["forward_limit_triggered"]
            if runtime_status_flags["reverse_limit_triggered"] != self.states["motor_1_reverse_limit_triggered"]:
                self.status_receiver("motor_1_reverse_limit_triggered",runtime_status_flags["reverse_limit_triggered"])
                self.states["motor_1_reverse_limit_triggered"] = runtime_status_flags["reverse_limit_triggered"]
            if runtime_status_flags["amps_trigger_activated"] != self.states["motor_1_amps_trigger_activated"]:
                self.status_receiver("motor_1_amps_trigger_activated",runtime_status_flags["amps_trigger_activated"])
                self.states["motor_1_amps_trigger_activated"] = runtime_status_flags["amps_trigger_activated"]
            time.sleep(self.period_s)

            runtime_status_flags = self.sdc.motor_2.get_runtime_status_flags()
            if runtime_status_flags["amps_limit_activated"] != self.states["motor_2_amps_limit_activated"]:
                self.status_receiver("motor_2_amps_limit_activated",runtime_status_flags["amps_limit_activated"])
                self.states["motor_2_amps_limit_activated"] = runtime_status_flags["amps_limit_activated"]
            if runtime_status_flags["motor_stalled"] != self.states["motor_2_motor_stalled"]:
                self.status_receiver("motor_2_motor_stalled",runtime_status_flags["motor_stalled"])
                self.states["motor_2_motor_stalled"] = runtime_status_flags["motor_stalled"]
            if runtime_status_flags["loop_error_detected"] != self.states["motor_2_loop_error_detected"]:
                self.status_receiver("motor_2_loop_error_detected",runtime_status_flags["loop_error_detected"])
                self.states["motor_2_loop_error_detected"] = runtime_status_flags["loop_error_detected"]
            if runtime_status_flags["safety_stop_active"] != self.states["motor_2_safety_stop_active"]:
                self.status_receiver("motor_2_safety_stop_active",runtime_status_flags["safety_stop_active"])
                self.states["motor_2_safety_stop_active"] = runtime_status_flags["safety_stop_active"]
            if runtime_status_flags["forward_limit_triggered"] != self.states["motor_2_forward_limit_triggered"]:
                self.status_receiver("motor_2_forward_limit_triggered",runtime_status_flags["forward_limit_triggered"])
                self.states["motor_2_forward_limit_triggered"] = runtime_status_flags["forward_limit_triggered"]
            if runtime_status_flags["reverse_limit_triggered"] != self.states["motor_2_reverse_limit_triggered"]:
                self.status_receiver("motor_2_reverse_limit_triggered",runtime_status_flags["reverse_limit_triggered"])
                self.states["motor_2_reverse_limit_triggered"] = runtime_status_flags["reverse_limit_triggered"]
            if runtime_status_flags["amps_trigger_activated"] != self.states["motor_2_amps_trigger_activated"]:
                self.status_receiver("motor_2_amps_trigger_activated",runtime_status_flags["amps_trigger_activated"])
                self.states["motor_2_amps_trigger_activated"] = runtime_status_flags["amps_trigger_activated"]
            time.sleep(self.period_s)

            runtime_fault_flags = self.sdc.get_runtime_fault_flags()
            if runtime_fault_flags is not None:
                if runtime_fault_flags["overheat"] != self.states["overheat"]:
                    #self.status_receiver("overheat",runtime_fault_flags["overheat"])
                    self.states["overheat"] = runtime_fault_flags["overheat"]
                if runtime_fault_flags["overvoltage"] != self.states["overvoltage"]:
                    #self.status_receiver("overvoltage",runtime_fault_flags["overvoltage"])
                    self.states["overvoltage"] = runtime_fault_flags["overvoltage"]
                if runtime_fault_flags["undervoltage"] != self.states["undervoltage"]:
                    #self.status_receiver("undervoltage",runtime_fault_flags["undervoltage"])
                    self.states["undervoltage"] = runtime_fault_flags["undervoltage"]
                if runtime_fault_flags["short_circuit"] != self.states["short_circuit"]:
                    #self.status_receiver("short_circuit",runtime_fault_flags["short_circuit"])
                    self.states["short_circuit"] = runtime_fault_flags["short_circuit"]
                if runtime_fault_flags["emergency_stop"] != self.states["emergency_stop"]:
                    #self.status_receiver("emergency_stop",runtime_fault_flags["emergency_stop"])
                    self.states["emergency_stop"] = runtime_fault_flags["emergency_stop"]
                if runtime_fault_flags["brushless_sensor_fault"] != self.states["brushless_sensor_fault"]:
                    #self.status_receiver("brushless_sensor_fault",runtime_fault_flags["brushless_sensor_fault"])
                    self.states["brushless_sensor_fault"] = runtime_fault_flags["brushless_sensor_fault"]
                if runtime_fault_flags["MOSFET_failure"] != self.states["MOSFET_failure"]:
                    #self.status_receiver("MOSFET_failure",runtime_fault_flags["MOSFET_failure"])
                    self.states["MOSFET_failure"] = runtime_fault_flags["MOSFET_failure"]
                if runtime_fault_flags["default_configuration_loaded_at_startup"] != self.states["default_configuration_loaded_at_startup"]:
                    #self.status_receiver("default_configuration_loaded_at_startup",runtime_fault_flags["default_configuration_loaded_at_startup"])
                    self.states["default_configuration_loaded_at_startup"] = runtime_fault_flags["default_configuration_loaded_at_startup"]

            """
            time.sleep(self.period_s)


#@capture_exceptions.Class
class Motor():
    """
    to do: can this class determine if/when a closed-loop goal is reached?
    to do: ^ including closed loop speed until position x?

    """
    # to do: can this class determine if/when a closed-loop goal is reached?
    #    when speed or position command is issued:
    #        check mode
    #        if closed loop speed:
    #            set polling bit
    #            poll speed until stably within x% of intended speed
    def __init__(
        self,
        add_to_queue,
        channel,
        motors_config,
        status_receiver
    ):
        self.add_to_queue = add_to_queue
        self.channel = channel
        self.motors_config = motors_config
        self.status_receiver = status_receiver
        self.bit_offset = int(self.channel) * 16
        self.target_reached = False
        self.target_value = 0
        self.queue = queue.Queue()
        self.states = {
            "MAC":None,
            "MDEC":None,
            "MMOD":None,
            "MVEL":None,
            "MXPF":None,
            "MXPR":None,
            "MXRPM":None,
            "ICAP":None,
            "KD":None,
            "KI":None,
            "KP":None,
            "BLFB":None,
            "EMOD":None,
            "EPPR":None,
            "CR":None,
            "ALIM":None,
            "ATGA":None,
            "ATGD":None,
            "ATRIG":None,
            "BLSTD":None,
            "CLERD":None,
            "EHL":None,
            "EHLA":None,
            "ELL":None,
            "ELLA":None,
            "P":None,
            "S":None,
            "A":None,
            "TR":None,
            "C":None,
            "F":None,
            "SR":None,
            "FS":None,
            "E":None,
            "FM":None,
            "T":None,
        }

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
        self.add_to_queue(serial_command)

    def get_motor_acceleration_rate(self, force_update = True):
        if self.states["MAC"] is None or force_update:
            event = threading.Event()
            serial_command = "~MAC {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_motor_acceleration_rate_)
            event.wait()
        return self.states["MAC"]

    def _store_motor_acceleration_rate_(self, success_bool, values_str, event):
        if success_bool:
            self.states["MAC"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def get_motor_deceleration_rate(self, force_update = True):
        if self.states["MDEC"] is None or force_update:
            event = threading.Event()
            serial_command = "~MDEC {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_motor_deceleration_rate_)
            event.wait()
        return self.states["MDEC"]

    def _store_motor_deceleration_rate_(self, success_bool, values_str, event):
        if success_bool:
            self.states["MDEC"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def get_operating_mode(self, force_update = True):
        if self.states["MMOD"] is None or force_update:
            event = threading.Event()
            serial_command = "~MMOD {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_operating_mode_)
            event.wait()
        return self.states["MMOD"]

    def _store_operating_mode_(self, success_bool, values_str, event):
        if success_bool:
            self.states["MMOD"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)


    def get_default_velocity_in_position_mode(self, force_update = True):
        if self.states["MVEL"] is None or force_update:
            event = threading.Event()
            serial_command = "~MVEL {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_default_velocity_in_position_mode_)
            event.wait()
        return self.states["MVEL"]

    def _store_default_velocity_in_position_mode_(self, success_bool, values_str, event):
        if success_bool:
            self.states["MVEL"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def get_max_power_forward(self, force_update = True):
        if self.states["MXPF"] is None or force_update:
            event = threading.Event()
            serial_command = "~MXPF {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_max_power_forward_)
            event.wait()
        return self.states["MXPF"]

    def _store_max_power_forward_(self, success_bool, values_str, event):
        if success_bool:
            self.states["MXPF"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)


    def get_max_power_reverse(self, force_update = True):
        if self.states["MXPR"] is None or force_update:
            event = threading.Event()
            serial_command = "~MXPR {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_max_power_reverse_)
            event.wait()
        return self.states["MXPR"]

    def _store_max_power_reverse_(self, success_bool, values_str, event):
        if success_bool:
            self.states["MXPR"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def get_max_rpm(self, force_update = True):
        if self.states["MXRPM"] is None or force_update:
            event = threading.Event()
            serial_command = "~MXRPM {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_max_rpm_)
            event.wait()
        return self.states["MXRPM"]

    def _store_max_rpm_(self, success_bool, values_str, event):
        if success_bool:
            self.states["MXRPM"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def go_to_absolute_position(self, position):
        """Description:
        This command is used in the Position Count mode to make the motor move to a specified
        encoder or hall count value.
        Syntax Serial:
        !P [cc] nn
        """
        serial_command = "!P {} {}".format(self.channel, position)
        self.add_to_queue(serial_command)

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
        self.add_to_queue(serial_command)

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
        self.add_to_queue(serial_command)

    def set_acceleration(self, acceleration): # 0-50000. Acceleration value is in 0.1 * RPM per second.  
        if acceleration > 500000:
            acceleration = 500000
        if acceleration < 0:
            acceleration = 0
        serial_command = "!AC {} {}".format(self.channel, acceleration)
        self.add_to_queue(serial_command)

    def set_deceleration(self, deceleration): # 0-50000. Acceleration value is in 0.1 * RPM per second.  
        if deceleration > 500000:
            deceleration = 500000
        if deceleration < 0:
            deceleration = 0
        serial_command = "!DC {} {}".format(self.channel, deceleration)
        self.add_to_queue(serial_command)

    def get_duty_cycle(self, force_update = True):
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
        if self.states["P"] is None or force_update:
            event = threading.Event()
            serial_command = "?P {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_duty_cycle_)
            event.wait()
        return self.states["P"]

    def _store_duty_cycle_(self, success_bool, values_str, event):
        if success_bool:
            self.states["P"] = values_str
        event.set()

    def get_motor_amps(self, force_update = True):
        """
        Measures and reports the motor Amps for all operating channels. Note that the current
        flowing through the motors is often higher than this flowing through the battery.
        """
        if self.states["A"] is None or force_update:
            event = threading.Event()
            serial_command = "?A {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_motor_amps_)
            event.wait()
        return self.states["A"]

    def _store_motor_amps_(self, success_bool, values_str, event):
        if success_bool:
            self.states["A"] = float(values_str)
        event.set()

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
        self.add_to_queue(serial_command)


    def get_pid_integral_cap(self, force_update = True):
        if self.states["ICAP"] is None or force_update:
            event = threading.Event()
            serial_command = "~ICAP {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_pid_integral_cap_)
            event.wait()
        return self.states["ICAP"]

    def _store_pid_integral_cap_(self, success_bool, values_str, event):
        if success_bool:
            self.states["ICAP"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def get_pid_differential_gain(self, force_update = True):
        if self.states["KD"] is None or force_update:
            event = threading.Event()
            serial_command = "~KD {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_pid_differential_gain_)
            event.wait()
        return self.states["KD"]

    def _store_pid_differential_gain_(self, success_bool, values_str, event):
        if success_bool:
            self.states["KD"] = float(values_str) / 10.0
        event.set()



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
        self.add_to_queue(serial_command)

    def get_pid_integral_gain(self, force_update = True):
        if self.states["KI"] is None or force_update:
            event = threading.Event()
            serial_command = "~KI {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_pid_integral_gain_)
            event.wait()
        return self.states["KI"]

    def _store_pid_integral_gain_(self, success_bool, values_str, event):
        if success_bool:
            self.states["KI"] = float(values_str) / 10.0
        event.set()

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
        self.add_to_queue(serial_command)

    def get_pid_proportional_gain(self, force_update = True):
        if self.states["KP"] is None or force_update:
            event = threading.Event()
            serial_command = "~KP {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_pid_proportional_gain_)
            event.wait()
        return self.states["KP"]

    def _store_pid_proportional_gain_(self, success_bool, values_str, event):
        if success_bool:
            self.states["KP"] = float(values_str) / 10.0
        event.set()


    ##############################################
    #    PID RUNTIME                             #
    ##############################################
    def get_expected_motor_position(self, force_update = True):
        """
        Reads the real-time value of the expected motor position in the position tracking closed
        loop mode and in speed position
        """
        if self.states["TR"] is None or force_update:
            event = threading.Event()
            serial_command = "?TR {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_expected_motor_position_)
            event.wait()
        return self.states["TR"]

    def _store_expected_motor_position_(self, success_bool, values_str, event):
        if success_bool:
            self.states["TR"] = values_str
        event.set()

    ##############################################
    #    ENCODERS SETUP                          #
    ##############################################

    def set_encoder_counter(self, value):
        serial_command = "!C {} {}".format(self.channel, value)
        self.add_to_queue(serial_command)

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
        self.add_to_queue(serial_command)

    def set_sensor_type_select_legacy(self, encoder_or_other_1, encoder_or_other_2):
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
        serial_command = "^BLFB {} {}".format(encoder_or_other_1, encoder_or_other_2)
        self.add_to_queue(serial_command)

    def get_sensor_type_select(self, force_update = True):
        if self.states["BLFB"] is None or force_update:
            event = threading.Event()
            serial_command = "~BLFB"
            self.add_to_queue(serial_command, event, self._store_sensor_type_select_)
            event.wait()
        return self.states["BLFB"]

    def _store_sensor_type_select_(self, success_bool, values_str, event):
        #print("_store_sensor_type_select_", repr(values_str))
        if success_bool:
            if values_str != "":
                values_a = values_str.split(":")
                self.states["BLFB"] = [int(values_a[0]),int(values_a[1])]
        event.set()

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
        self.add_to_queue(serial_command)

    def get_encoder_usage(self, force_update = True):
        if self.states["EMOD"] is None or force_update:
            event = threading.Event()
            serial_command = "~EMOD {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_usage_)
            event.wait()
        return self.states["EMOD"]

    def _store_encoder_usage_(self, success_bool, values_str, event):
        if success_bool:
            self.states["EMOD"] = int(values_str) - self.bit_offset
        event.set()

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
        self.add_to_queue(serial_command)

    def get_encoder_ppr_value(self, force_update = True):
        if self.states["EPPR"] is None or force_update:
            event = threading.Event()
            serial_command = "~EPPR {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_ppr_value_)
            event.wait()
        return self.states["EPPR"]

    def _store_encoder_ppr_value_(self, success_bool, values_str, event):
        if success_bool:
            self.states["EPPR"] = int(values_str)
        event.set()

    ##############################################
    #    ENCODERS RUNTIME                        #
    ##############################################

    def get_encoder_counter_absolute(self, force_update = True):
        """
        Returns the encoder value as an absolute number. The counter is 32-bit with a range of
        +/- 2147483648 counts.

        Type: Signed 32-bit
        Min: -2147M
        Max: 2147M
        """
        if self.states["C"] is None or force_update:
            event = threading.Event()
            serial_command = "?C {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_counter_absolute_)
        return int(self.states["C"])

    def _store_encoder_counter_absolute_(self, success_bool, values_str, event):
        #print("_store_encoder_counter_absolute_",values_str,event)
        if success_bool:
            self.states["C"] = values_str
        event.set()

    def get_feedback(self, force_update = True):
        """
        Reports the value of the feedback sensors that are associated to each of the channels in
        closed-loop modes. The feedback source can be Encoder, Analog or Pulse. Selecting the
        feedback source is done using the encoder, pulse or analog configuration parameters. This
        query is useful for verifying that the correct feedback source is used by the channel in the
        closed-loop mode and that its value is in range with expectations.
        """
        if self.states["F"] is None or force_update:
            event = threading.Event()
            serial_command = "?F {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_feedback_)
            event.wait()
        return self.states["F"]

    def _store_feedback_(self, success_bool, values_str, event):
        if success_bool:
            self.states["F"] = values_str
        event.set()

    def get_encoder_counter_relative(self, force_update = True):
        """
        Returns the amount of counts that have been measured from the last time this query was
        made. Relative counter read is sometimes easier to work with, compared to full counter
        reading, as smaller numbers are usually returned.
        """
        if self.states["CR"] is None or force_update:
            event = threading.Event()
            serial_command = "?CR {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_counter_relative_)
        return int(self.states["CR"])

    def _store_encoder_counter_relative_(self, success_bool, values_str, event):
        if success_bool:
            self.states["CR"] = values_str
        event.set()


    def get_encoder_motor_speed_in_rpm(self, force_update = True):
        """
        Reports the actual speed measured by the encoders as the actual RPM value. To report
        RPM accurately, the correct Pulses per Revolution (PPR) must be
        """
        if self.states["S"] is None or force_update:
            event = threading.Event()
            serial_command = "?S {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_motor_speed_in_rpm_)
            event.wait()
        return self.states["S"]

    def _store_encoder_motor_speed_in_rpm_(self, success_bool, values_str, event):
        if success_bool:
            self.states["S"] = values_str
        event.set()


    def get_encoder_speed_relative(self, force_update = True):
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
        if self.states["SR"] is None or force_update:
            event = threading.Event()
            serial_command = "?SR {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_speed_relative_)
            event.wait()
        return self.states["SR"]

    def _store_encoder_speed_relative_(self, success_bool, values_str, event):
        if success_bool:
            self.states["SR"] = values_str
        event.set()



    ##############################################
    #    SAFETY                                  #
    ##############################################
    def stop(self):
        serial_command = "!MS {}".format(self.channel)
        self.add_to_queue(serial_command)

    def get_config_flags(self, force_update = True):
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
        if self.states["FS"] is None or force_update:
            event = threading.Event()
            serial_command = "?FS {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_config_flags_)
            event.wait()
        return self.states["FS"]

    def _store_config_flags_(self, success_bool, values_str, event):
        if success_bool:
            self.states["FS"] = values_str
        event.set()

    def set_current_limit(self, amps):
        serial_command = "^ALIM {} {}".format(self.channel, amps * 10)
        self.add_to_queue(serial_command)

    def get_current_limit(self, force_update = True):
        if self.states["ALIM"] is None or force_update:
            event = threading.Event()
            serial_command = "~ALIM {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_current_limit_)
            event.wait()
        return self.states["ALIM"]

    def _store_current_limit_(self, success_bool, values_str, event):
        if success_bool:
            self.states["ALIM"] = float(values_str) / 10.0
        event.set()

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
        self.add_to_queue(serial_command)

    def get_current_limit_action(self, force_update = True):
        if self.states["ATGA"] is None or force_update:
            event = threading.Event()
            serial_command = "~ATGA {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_current_limit_action_)
            event.wait()
        return self.states["ATGA"]

    def _store_current_limit_action_(self, success_bool, values_str, event):
        if success_bool:
            self.states["ATGA"] = int(values_str)
        event.set()

    def set_current_limit_min_period(self, milliseconds):
        """
        This parameter contains the time in milliseconds during which the Amps Trigger Level
        (ATRIG) must be exceeded before the Amps Trigger Action (ATGA) is called. This parame-
        ter is used to prevent Amps Trigger Actions to be taken in case of short duration spikes.
        """
        serial_command = "^ATGD {} {}".format(self.channel, milliseconds)
        self.add_to_queue(serial_command)

    def get_current_limit_min_period(self, force_update = True):
        if self.states["ATGD"] is None or force_update:
            event = threading.Event()
            serial_command = "~ATGD {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_current_limit_min_period_)
            event.wait()
        return self.states["ATGD"]

    def _store_current_limit_min_period_(self, success_bool, values_str, event):
        if success_bool:
            self.states["ATGD"] = int(values_str)
        event.set()




    def set_current_limit_amps(self, amps):
        """
        This parameter lets you select Amps threshold value that will trigger an action. This
        threshold must be set to be below the ALIM Amps limit. When that threshold is reached,
        then list of action can be selected using the ATGA parameter
        """
        serial_command = "^ATRIG {} {}".format(self.channel, amps*10)
        self.add_to_queue(serial_command)

    def get_current_limit_amps(self, force_update = True):
        if self.states["ATRIG"] is None or force_update:
            event = threading.Event()
            serial_command = "~ATRIG {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_current_limit_amps_)
            event.wait()
        return self.states["ATRIG"]

    def _store_current_limit_amps_(self, success_bool, values_str, event):
        if success_bool:
            self.states["ATRIG"] = float(values_str) / 10.0
        event.set()

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
        self.add_to_queue(serial_command)

    def get_stall_detection(self, force_update = True):
        if self.states["BLSTD"] is None or force_update:
            event = threading.Event()
            serial_command = "~BLSTD {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_stall_detection_)
            event.wait()
        return self.states["BLSTD"]

    def _store_stall_detection_(self, success_bool, values_str, event):
        if success_bool:
            self.states["BLSTD"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def get_closed_loop_error_detection(self, force_update = True):
        if self.states["CLERD"] is None or force_update:
            event = threading.Event()
            serial_command = "~CLERD {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_closed_loop_error_detection_)
            event.wait()
        return self.states["CLERD"]

    def _store_closed_loop_error_detection_(self, success_bool, values_str, event):
        if success_bool:
            self.states["CLERD"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def get_encoder_high_count_limit(self, force_update = True):
        if self.states["EHL"] is None or force_update:
            event = threading.Event()
            serial_command = "~EHL {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_high_count_limit_)
            event.wait()
        return self.states["EHL"]

    def _store_encoder_high_count_limit_(self, success_bool, values_str, event):
        if success_bool:
            self.states["EHL"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def get_encoder_high_limit_action(self, force_update = True):
        if self.states["EHLA"] is None or force_update:
            event = threading.Event()
            serial_command = "~EHLA {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_high_limit_action_)
            event.wait()
        return self.states["EHLA"]

    def _store_encoder_high_limit_action_(self, success_bool, values_str, event):
        if success_bool:
            self.states["EHLA"] = int(values_str) - self.bit_offset
        event.set()

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
        self.add_to_queue(serial_command)

    def get_encoder_low_count_limit(self, force_update = True):
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
        if self.states["ELL"] is None or force_update:
            event = threading.Event()
            serial_command = "~ELL {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_low_count_limit_)
            event.wait()
        return self.states["ELL"]

    def _store_encoder_low_count_limit_(self, success_bool, values_str, event):
        if success_bool:
            self.states["ELL"] = int(values_str)
        event.set()

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
        self.add_to_queue(serial_command)

    def get_encoder_low_limit_action(self, force_update = True):
        """
        In closed-loop modes, returns the difference between the desired speed or position and
        the measured feedback. This query can be used to detect when the motor has reached
        the desired speed or position. In open loop mode, this query returns 0.
        """
        if self.states["ELLA"] is None or force_update:
            event = threading.Event()
            serial_command = "~ELLA {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_encoder_low_limit_action_)
            event.wait()
        return self.states["ELLA"]

    def _store_encoder_low_limit_action_(self, success_bool, values_str, event):
        if success_bool:
            self.states["ELLA"] = int(values_str)
        event.set()

    def get_closed_loop_error(self, force_update = True):
        """
        In closed-loop modes, returns the difference between the desired speed or position and
        the measured feedback. This query can be used to detect when the motor has reached
        the desired speed or position. In open loop mode, this query returns 0.
        """
        if self.states["E"] is None or force_update:
            event = threading.Event()
            serial_command = "?E {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_closed_loop_error_)
            event.wait()
        return self.states["E"]

    def _store_closed_loop_error_(self, success_bool, values_str, event):
        if success_bool:
            self.states["E"] = int(values_str)
        event.set()

    def get_runtime_status_flags(self, force_update = True):
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
        if self.states["FM"] is None or force_update:
            event = threading.Event()
            serial_command = "?FM {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_runtime_status_flags_)
            event.wait()
        return self.states["FM"]

    def _store_runtime_status_flags_(self, success_bool, values_str, event):
        if success_bool:
            values_int = int(values_str)
            self.states["FM"] = {
                "amps_limit_activated":self._get_bit_(values_int, 0),
                "motor_stalled":self._get_bit_(values_int, 1),
                "loop_error_detected":self._get_bit_(values_int, 2),
                "safety_stop_active":self._get_bit_(values_int, 3),
                "forward_limit_triggered":self._get_bit_(values_int, 4),
                "reverse_limit_triggered":self._get_bit_(values_int, 5),
                "amps_trigger_activated":self._get_bit_(values_int, 6),
            }
        event.set()

    def get_temperature(self, force_update = True):
        """
        Reports the temperature at each of the Heatsink sides and on the internal MCU silicon
        chip. The reported value is in degrees C with a one degree resolution.

        Reply:
            T= cc
            Type: Signed 8-bit Min: -40 Max: 125
        """
        if self.states["T"] is None or force_update:
            event = threading.Event()
            serial_command = "?T {}".format(self.channel)
            self.add_to_queue(serial_command, event, self._store_temperature_)
            event.wait()
        return self.states["T"]

    def _store_temperature_(self, success_bool, values_str, event):
        if success_bool:
            channel_1, channel_2 = values_str.split(":")
            self.states["T"] = [int(channel_1),int(channel_2)]
        event.set()

    ##############################################
    #    CLASS INTERNALS                         #
    ##############################################

    def _get_bit_(self, number, place):
        return (number & (1 << place)) >> place




#@capture_exceptions.Class
class SDC(threading.Thread):
    def __init__(
            self, 
            data_receiver, 
            status_receiver, 
            exception_receiver,
            config={}, 
            serial_device_path_patterns=['/dev/serial/by-id/usb-FTDI*','/dev/serial/by-id/usb-Roboteq*']):
        threading.Thread.__init__(self)

        self.data_receiver = data_receiver
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.config = config
        self.serial_device_path_patterns = serial_device_path_patterns
        self.queue = queue.Queue()
        self.device_connected = False

        self.motor_1 = Motor(
            self.add_to_queue,
            1,
            self.config,
            self.status_receiver
        )
        self.motor_2 = Motor(
            self.add_to_queue,
            2,
            self.config,
            self.status_receiver
        )

        self.serial_device_paths = self.get_device_id_list()
        if len(self.serial_device_paths) == 0:
            self.status_receiver("aborting: no matching serial adapter found",self.serial_device_paths)
            return
        if len(self.serial_device_paths) > 1:
            self.status_receiver("aborting:  This library supports only one controller at a time. Found", self.serial_device_paths)
            return
        self.serial = serial.Serial(
            port=self.serial_device_paths[0],
            baudrate=115200,
            timeout=0.2,
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
            "FID":None,
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
        self.start()
        self.status_poller = Status_Poller(
            self, 
            data_receiver, 
            status_receiver, 
            exception_receiver
        )
        self.status_poller.start()


    def get_device_connected(self):
        # warning: this may not be threadsafe
        return self.device_connected


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

    def get_mixed_mode(self, force_update = True):
        if self.states["MXMD"] is None or force_update:
            event = threading.Event()
            serial_command = "~MXMD"
            self.add_to_queue(serial_command, event, self._store_mixed_mode_)
            event.wait()
        return self.states["MXMD"]

    def _store_mixed_mode_(self, success_bool, values_str, event):
        if success_bool:
            self.states["MXMD"] = 0 if values_str == "0:0" else 1
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

    def get_pwm_frequency(self, force_update = True):
        if self.states["PWMF"] is None or force_update:
            event = threading.Event()
            serial_command = "~PWMF"
            self.add_to_queue(serial_command, event, self._store_pwm_frequency_)
            event.wait()
        return self.states["PWMF"]

    def _store_pwm_frequency_(self, success_bool, values_str, event):
        if success_bool:
            self.states["PWMF"] = int(values_str)
        event.set()


    ##############################################
    #    SAFETY                                  #
    ##############################################

    def get_runtime_fault_flags(self, force_update = True):
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

    def _store_runtime_fault_flags_(self, success_bool, values_str, event):
        if success_bool:
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

    def get_volts(self, force_update = True):
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

    def _store_volts_(self, success_bool, values_str, event):
        if success_bool:
            self.states["V"] = values_str
        event.set()

    def emergency_stop(self):
        serial_command = "!EX"
        self.add_to_queue(serial_command)

    def emergency_stop_release(self):
        serial_command = "!MG"
        self.add_to_queue(serial_command)

    def set_emergency_stop(self, value_bool):
        if value_bool:
            print("set_emergency_stop 1",value_bool)
            self.emergency_stop()
        else:
            print("set_emergency_stop 2",value_bool)
            self.emergency_stop_release()

    def get_emergency_stop(self):
        runtime_fault_flags = self.get_runtime_fault_flags()
        print("emergency_stop", runtime_fault_flags)
        if runtime_fault_flags["emergency_stop"] == 1:
            return True
        else:
            return False

    def set_serial_data_watchdog(self, miliseconds):
        serial_command = "^RWD {}".format(miliseconds)
        self.add_to_queue(serial_command)

    def get_serial_data_watchdog(self, force_update = True):
        if self.states["RWD"] is None or force_update:
            event = threading.Event()
            serial_command = "~RWD"
            self.add_to_queue(serial_command, event, self._store_serial_data_watchdog_)
            event.wait()
        return self.states["RWD"]

    def _store_serial_data_watchdog_(self, success_bool, values_str, event):
        if success_bool:
            self.states["RWD"] = int(values_str)
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


    def get_overvoltage_hysteresis(self, force_update = True):
        if self.states["OVH"] is None or force_update:
            event = threading.Event()
            serial_command = "~OVH"
            self.add_to_queue(serial_command, event, self._store_overvoltage_hysteresis_)
            event.wait()
        return self.states["OVH"]

    def _store_overvoltage_hysteresis_(self, success_bool, values_str, event):
        if success_bool:
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

    def get_overvoltage_cutoff_threhold(self, force_update = True):
        if self.states["OVL"] is None or force_update:
            event = threading.Event()
            serial_command = "~OVL"
            self.add_to_queue(serial_command, event, self._store_overvoltage_cutoff_threhold_)
            event.wait()
        return self.states["OVL"]

    def _store_overvoltage_cutoff_threhold_(self, success_bool, values_str, event):
        if success_bool:
            self.states["OVL"] = float(values_str) / 10.0
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

    def get_short_circuit_detection_threshold(self, force_update = True):
        if self.states["THLD"] is None or force_update:
            event = threading.Event()
            serial_command = "~THLD"
            self.add_to_queue(serial_command, event, self._store_short_circuit_detection_threshold_)
            event.wait()
        return self.states["THLD"]

    def _store_short_circuit_detection_threshold_(self, success_bool, values_str, event):
        if success_bool:
            self.states["THLD"] = int(values_str)
        event.set()

    def set_undervoltage_limit(self,volts):
        """
        Sets the voltage below which the controller will turn off its power stage. The voltage is
        entered as a desired voltage value multiplied by 10. Undervoltage condition is cleared as
        soon as voltage rises above the limit.
        """
        serial_command = "^UVL {}".format(volts*10)
        self.add_to_queue(serial_command)

    def get_undervoltage_limit(self, force_update = True):
        if self.states["UVL"] is None or force_update:
            event = threading.Event()
            serial_command = "~UVL"
            self.add_to_queue(serial_command, event, self._store_undervoltage_limit_)
            event.wait()
        return self.states["UVL"]

    def _store_undervoltage_limit_(self, success_bool, values_str, event):
        if success_bool:
            self.states["UVL"] = int(values_str)
        event.set()

    def set_brake_activation_delay(self,miliseconds):
        """
        Set the delay in miliseconds from the time a motor stops and the time an output connect-
        ed to a brake solenoid will be released. Applies to any Digital Ouput(s) that is configured
        as motor brake. Delay value applies to all motors in multi-channel products.
        """
        serial_command = "^BKD {}".format(miliseconds)
        self.add_to_queue(serial_command)

    def get_brake_activation_delay(self, force_update = True):
        if self.states["BKD"] is None or force_update:
            event = threading.Event()
            serial_command = "~BKD"
            self.add_to_queue(serial_command, event, self._store_brake_activation_delay_)
            event.wait()
        return self.states["BKD"]

    def _store_brake_activation_delay_(self, success_bool, values_str, event):
        if success_bool:
            self.states["BKD"] = int(values_str)
        event.set()


    def set_digital_out_bits(self, output_number): # -500,000 to 500,000
        """
        Description:
        D1 - Set Individual Digital Out bits
        Description:
        The D1 command will activate the single digital output that is selected by the parameter
        that follows.
        Syntax Serial:
        !D1 nn
        Where:
        nn = Output number
        Example:
        !D1 1 : will activate output 1
        """
        # warning: this is a hack. connect/disconnect flow needs refactoring
        if self.device_connected:
            serial_command = "!D1 {} ".format(output_number)
            self.add_to_queue(serial_command)


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

    def get_command_priorities(self, force_update = True):
        if self.states["CPRI"] is None or force_update:
            event = threading.Event()
            serial_command = "~CPRI"
            self.add_to_queue(serial_command, event, self._store_command_priorities_)
            event.wait()
        return self.states["CPRI"]

    def _store_command_priorities_(self, success_bool, values_str, event):
        if success_bool:
            values_a = values_str.split(":")
            self.states["CPRI"] = values_a
        event.set()

    def set_serial_echo(self, enable_disable):
        """
        enable_disable: :
            0: Echo is enabled
            1: Echo is disabled
        """
        serial_command = "^ECHOF {}".format(enable_disable)
        self.add_to_queue(serial_command)

    def get_serial_echo(self, force_update = True):
        if self.states["ECHOF"] is None or force_update:
            event = threading.Event()
            serial_command = "~ECHOF"
            self.add_to_queue(serial_command, event, self._store_serial_echo_)
            event.wait()
        return self.states["ECHOF"]

    def _store_serial_echo_(self, success_bool, values_str, event):
        if success_bool:
            self.states["ECHOF"] = int(values_str)
        event.set()

    def set_rs232_bit_rate(self, bit_rate_code):
        """
        bit_rate_code =
            0: 115200
            1: 57600
            2: 38400
            3: 19200
            4: 9600
            5: 115200 + Inverted RS232
            6: 57600 + Inverted RS232
            7: 38400 + Inverted RS232
            8: 19200 + Inverted RS232
            9: 9600 + Inverted RS232
        """
        serial_command = "^RSBR {}".format(bit_rate_code)
        self.add_to_queue(serial_command)

    def get_rs232_bit_rate(self, force_update = True):
        if self.states["RSBR"] is None or force_update:
            event = threading.Event()
            serial_command = "~RSBR"
            self.add_to_queue(serial_command, event, self._store_rs232_bit_rate_)
            event.wait()
        return self.states["RSBR"]

    def _store_rs232_bit_rate_(self, success_bool, values_str, event):
        if success_bool:
            self.states["RSBR"] = values_str
        event.set()

    ##############################################
    #    MEMORY                                  #
    ##############################################

    def get_mcu_id(self, force_update = True):
        if self.states["UID"] is None or force_update:
            event = threading.Event()
            serial_command = "?UID"
            self.add_to_queue(serial_command, event, self._store_mcu_id_)
            event.wait()
        return self.states["UID"]

    def _store_mcu_id_(self, success_bool, values_str, event):
        if success_bool:
            self.states["UID"] = values_str
            self.mcu_id = values_str
        event.set()

    def get_firmware_version(self, force_update = True):
        if self.states["FID"] is None or force_update:
            event = threading.Event()
            serial_command = "?FID"
            self.add_to_queue(serial_command, event, self._store_firmware_version_)
            event.wait()
        return self.states["FID"]

    def _store_firmware_version_(self, success_bool, values_str, event):
        if success_bool:
            self.states["FID"] = values_str
            self.mcu_id = values_str
        event.set()

    def set_user_boolean_variable(self, position, value):
        serial_command = "!B {} {}".format(position, value)
        self.add_to_queue(serial_command)

    def get_user_boolean_value(self, position, force_update = True):
        if self.states["B"] is None or force_update:
            event = threading.Event()
            serial_command = "?B"
            self.add_to_queue(serial_command, event, self._store_user_boolean_value_)
            event.wait()
        return self.states["B"]

    def _store_user_boolean_value_(self, success_bool, values_str, event):
        if success_bool:
            self.states["B"] = values_str
        event.set()

    def set_user_variable(self, position, value):
        serial_command = "!VAR {} {}".format(position, value)
        self.add_to_queue(serial_command)

    def get_user_variable(self, position, force_update = True):
        if self.states["VAR"] is None or force_update:
            event = threading.Event()
            serial_command = "?VAR"
            self.add_to_queue(serial_command, event, self._store_user_variable_)
            event.wait()
        return self.states["VAR"]

    def _store_user_variable_(self, success_bool, values_str, event):
        if success_bool:
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

    def get_user_data_in_ram(self, force_update = True):
        if self.states["EE"] is None or force_update:
            event = threading.Event()
            serial_command = "~EE"
            self.add_to_queue(serial_command, event, self._store_user_data_in_ram_)
            event.wait()
        return self.states["EE"]

    def _store_user_data_in_ram_(self, success_bool, values_str, event):
        if success_bool:
            self.states["EE"] = values_str
        event.set()


    def save_configuration_in_eeprom(self):
        serial_command = "%EESAV"
        #serial_command = "!EES"
        self.add_to_queue(serial_command)

    def get_lock_status(self, force_update = True):
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

    def _store_lock_status_(self, success_bool, values_str, event):
        if success_bool:
            self.states["LK"] = int(values_str)
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

    def get_script_auto_start(self, force_update = True):
        if self.states["BRUN"] is None or force_update:
            event = threading.Event()
            serial_command = "~BRUN"
            self.add_to_queue(serial_command, event, self._store_script_auto_start_)
            event.wait()
        return self.states["BRUN"]

    def _store_script_auto_start_(self, success_bool, values_str, event):
        if success_bool:
            self.states["BRUN"] = int(values_str)
        event.set()

    def run_script(self):
        serial_command = "!R"
        self.add_to_queue

    ##############################################
    #    READ AND APPLY CONFIG                   #
    ##############################################

    def read_config_from_sdc(self):
        return {
            "brake_activation_delay":self.get_brake_activation_delay(True),
            "command_priorities":self.get_command_priorities(True),
            "lock_status":self.get_lock_status(True),
            "mixed_mode":self.get_mixed_mode(True),
            "overvoltage_cutoff_threhold":self.get_overvoltage_cutoff_threhold(True),
            #"overvoltage_hysteresis":self.get_overvoltage_hysteresis(True),
            "pwm_frequency":self.get_pwm_frequency(True),
            #"rs232_bit_rate":self.get_rs232_bit_rate(True),
            #"runtime_fault_flags":self.get_runtime_fault_flags(True),
            "script_auto_start":self.get_script_auto_start(True),
            "serial_data_watchdog":self.get_serial_data_watchdog(True),
            "serial_echo":self.get_serial_echo(True),
            "short_circuit_detection_threshold":self.get_short_circuit_detection_threshold(True),
            "undervoltage_limit":self.get_undervoltage_limit(True),
            #"user_boolean_value":self.get_user_boolean_value(True),
            #"user_variable":self.get_user_variable(True),
            #"volts":self.get_volts(True),
            "motor_1":{
                "closed_loop_error_detection":self.motor_1.get_closed_loop_error_detection(True),
                "current_limit":self.motor_1.get_current_limit(True),
                "current_limit_action":self.motor_1.get_current_limit_action(True),
                "current_limit_amps":self.motor_1.get_current_limit_amps(True),
                "current_limit_min_period":self.motor_1.get_current_limit_min_period(True),
                "default_velocity_in_position_mode":self.motor_1.get_default_velocity_in_position_mode(True),
                "encoder_high_count_limit":self.motor_1.get_encoder_high_count_limit(True),
                "encoder_high_limit_action":self.motor_1.get_encoder_high_limit_action(True),
                "encoder_low_count_limit":self.motor_1.get_encoder_low_count_limit(True),
                "encoder_low_limit_action":self.motor_1.get_encoder_low_limit_action(True),
                "encoder_ppr_value":self.motor_1.get_encoder_ppr_value(True),
                "encoder_usage":self.motor_1.get_encoder_usage(True),
                "max_power_forward":self.motor_1.get_max_power_forward(True),
                "max_power_reverse":self.motor_1.get_max_power_reverse(True),
                "max_rpm":self.motor_1.get_max_rpm(True),
                "motor_acceleration_rate":self.motor_1.get_motor_acceleration_rate(True),
                "motor_deceleration_rate":self.motor_1.get_motor_deceleration_rate(True),
                "operating_mode":self.motor_1.get_operating_mode(True),
                "pid_differential_gain":self.motor_1.get_pid_differential_gain(True),
                "pid_integral_cap":self.motor_1.get_pid_integral_cap(True),
                "pid_integral_gain":self.motor_1.get_pid_integral_gain(True),
                "pid_proportional_gain":self.motor_1.get_pid_proportional_gain(True),
                "sensor_type_select":self.motor_1.get_sensor_type_select(True),
                "stall_detection":self.motor_1.get_stall_detection(True),
            },
            "motor_2":{
                "closed_loop_error_detection":self.motor_2.get_closed_loop_error_detection(True),
                "current_limit":self.motor_2.get_current_limit(True),
                "current_limit_action":self.motor_2.get_current_limit_action(True),
                "current_limit_amps":self.motor_2.get_current_limit_amps(True),
                "current_limit_min_period":self.motor_2.get_current_limit_min_period(True),
                "default_velocity_in_position_mode":self.motor_2.get_default_velocity_in_position_mode(True),
                "encoder_high_count_limit":self.motor_2.get_encoder_high_count_limit(True),
                "encoder_high_limit_action":self.motor_2.get_encoder_high_limit_action(True),
                "encoder_low_count_limit":self.motor_2.get_encoder_low_count_limit(True),
                "encoder_low_limit_action":self.motor_2.get_encoder_low_limit_action(True),
                "encoder_ppr_value":self.motor_2.get_encoder_ppr_value(True),
                "encoder_usage":self.motor_2.get_encoder_usage(True),
                "max_power_forward":self.motor_2.get_max_power_forward(True),
                "max_power_reverse":self.motor_2.get_max_power_reverse(True),
                "max_rpm":self.motor_2.get_max_rpm(True),
                "motor_acceleration_rate":self.motor_2.get_motor_acceleration_rate(True),
                "motor_deceleration_rate":self.motor_2.get_motor_deceleration_rate(True),
                "operating_mode":self.motor_2.get_operating_mode(True),
                "pid_differential_gain":self.motor_2.get_pid_differential_gain(True),
                "pid_integral_cap":self.motor_2.get_pid_integral_cap(True),
                "pid_integral_gain":self.motor_2.get_pid_integral_gain(True),
                "pid_proportional_gain":self.motor_2.get_pid_proportional_gain(True),
                "sensor_type_select":self.motor_2.get_sensor_type_select(True),
                "stall_detection":self.motor_2.get_stall_detection(True),
            }
        }


    def apply_config_to_sdc(self, config, save=True):
        self.emergency_stop()
        # apply emergency stop
        for config_entry in config:
            print(config_entry)
            if config_entry=="brake_activation_delay":
                self.set_brake_activation_delay(config[config_entry])
            #if config_entry=="command_priorities":
            #    self.set_command_priorities(config[config_entry])
            #if config_entry=="lock_status":
            #    self.set_lock_status(config[config_entry])
            #if config_entry=="mixed_mode":
            #    self.set_mixed_mode(config[config_entry])
            if config_entry=="overvoltage_cutoff_threhold":
                self.set_overvoltage_cutoff_threhold(config[config_entry])
            if config_entry=="pwm_frequency":
                self.set_pwm_frequency(config[config_entry])
            if config_entry=="script_auto_start":
                self.set_script_auto_start(config[config_entry])
            if config_entry=="serial_data_watchdog":
                self.set_serial_data_watchdog(config[config_entry])
            if config_entry=="serial_echo":
                self.set_serial_echo(config[config_entry])
            if config_entry=="short_circuit_detection_threshold":
                self.set_short_circuit_detection_threshold(config[config_entry])
            if config_entry=="undervoltage_limit":
                self.set_undervoltage_limit(config[config_entry])
            #if config_entry=="user_boolean_value":
            #    self.set_user_boolean_value(config[config_entry])
            #if config_entry=="user_variable":
            #    self.set_user_variable(config[config_entry])

        # to do: specific write formats must be finished 

        for config_entry in config["motor_1"]:
            print(config_entry)
            if config_entry=="closed_loop_error_detection":
                self.motor_1.set_closed_loop_error_detection(config["motor_1"][config_entry])
            if config_entry=="current_limit":
                self.motor_1.set_current_limit(config["motor_1"][config_entry])
            if config_entry=="current_limit_action":
                self.motor_1.set_current_limit_action(config["motor_1"][config_entry])
            if config_entry=="current_limit_amps":
                self.motor_1.set_current_limit_amps(config["motor_1"][config_entry])
            if config_entry=="current_limit_min_period":
                self.motor_1.set_current_limit_min_period(config["motor_1"][config_entry])
            if config_entry=="default_velocity_in_position_mode":
                self.motor_1.set_default_velocity_in_position_mode(config["motor_1"][config_entry])
            if config_entry=="encoder_high_count_limit":
                self.motor_1.set_encoder_high_count_limit(config["motor_1"][config_entry])
            if config_entry=="encoder_high_limit_action":
                self.motor_1.set_encoder_high_limit_action(config["motor_1"][config_entry])
            if config_entry=="encoder_low_count_limit":
                self.motor_1.set_encoder_low_count_limit(config["motor_1"][config_entry])
            if config_entry=="encoder_low_limit_action":
                self.motor_1.set_encoder_low_limit_action(config["motor_1"][config_entry])
            if config_entry=="encoder_ppr_value":
                self.motor_1.set_encoder_ppr_value(config["motor_1"][config_entry])
            if config_entry=="encoder_usage":
                self.motor_1.set_encoder_usage(config["motor_1"][config_entry])
            if config_entry=="max_power_forward":
                self.motor_1.set_max_power_forward(config["motor_1"][config_entry])
            if config_entry=="max_power_reverse":
                self.motor_1.set_max_power_reverse(config["motor_1"][config_entry])
            if config_entry=="max_rpm":
                self.motor_1.set_max_rpm(config["motor_1"][config_entry])
            if config_entry=="motor_acceleration_rate":
                self.motor_1.set_motor_acceleration_rate(config["motor_1"][config_entry])
            if config_entry=="motor_deceleration_rate":
                self.motor_1.set_motor_deceleration_rate(config["motor_1"][config_entry])
            if config_entry=="operating_mode":
                self.motor_1.set_operating_mode(config["motor_1"][config_entry])
            if config_entry=="pid_differential_gain":
                self.motor_1.set_pid_differential_gain(config["motor_1"][config_entry])
            if config_entry=="pid_integral_cap":
                self.motor_1.set_pid_integral_cap(config["motor_1"][config_entry])
            if config_entry=="pid_integral_gain":
                self.motor_1.set_pid_integral_gain(config["motor_1"][config_entry])
            if config_entry=="pid_proportional_gain":
                self.motor_1.set_pid_proportional_gain(config["motor_1"][config_entry])
            if config_entry=="sensor_type_select":
                print("self.motor_1.set_sensor_type_select(0)")
                self.motor_1.set_sensor_type_select(0)
                #self.motor_1.set_sensor_type_select(config["motor_1"][config_entry][0])
            if config_entry=="stall_detection":
                self.motor_1.set_stall_detection(config["motor_1"][config_entry])

        for config_entry in config["motor_2"]:
            print(config_entry)
            if config_entry=="closed_loop_error_detection":
                self.motor_2.set_closed_loop_error_detection(config["motor_2"][config_entry])
            if config_entry=="current_limit":
                self.motor_2.set_current_limit(config["motor_2"][config_entry])
            if config_entry=="current_limit_action":
                self.motor_2.set_current_limit_action(config["motor_2"][config_entry])
            if config_entry=="current_limit_amps":
                self.motor_2.set_current_limit_amps(config["motor_2"][config_entry])
            if config_entry=="current_limit_min_period":
                self.motor_2.set_current_limit_min_period(config["motor_2"][config_entry])
            if config_entry=="default_velocity_in_position_mode":
                self.motor_2.set_default_velocity_in_position_mode(config["motor_2"][config_entry])
            if config_entry=="encoder_high_count_limit":
                self.motor_2.set_encoder_high_count_limit(config["motor_2"][config_entry])
            if config_entry=="encoder_high_limit_action":
                self.motor_2.set_encoder_high_limit_action(config["motor_2"][config_entry])
            if config_entry=="encoder_low_count_limit":
                self.motor_2.set_encoder_low_count_limit(config["motor_2"][config_entry])
            if config_entry=="encoder_low_limit_action":
                self.motor_2.set_encoder_low_limit_action(config["motor_2"][config_entry])
            if config_entry=="encoder_ppr_value":
                self.motor_2.set_encoder_ppr_value(config["motor_2"][config_entry])
            if config_entry=="encoder_usage":
                self.motor_2.set_encoder_usage(config["motor_2"][config_entry])
            if config_entry=="max_power_forward":
                self.motor_2.set_max_power_forward(config["motor_2"][config_entry])
            if config_entry=="max_power_reverse":
                self.motor_2.set_max_power_reverse(config["motor_2"][config_entry])
            if config_entry=="max_rpm":
                self.motor_2.set_max_rpm(config["motor_2"][config_entry])
            if config_entry=="motor_acceleration_rate":
                self.motor_2.set_motor_acceleration_rate(config["motor_2"][config_entry])
            if config_entry=="motor_deceleration_rate":
                self.motor_2.set_motor_deceleration_rate(config["motor_2"][config_entry])
            if config_entry=="operating_mode":
                self.motor_2.set_operating_mode(config["motor_2"][config_entry])
            if config_entry=="pid_differential_gain":
                self.motor_2.set_pid_differential_gain(config["motor_2"][config_entry])
            if config_entry=="pid_integral_cap":
                self.motor_2.set_pid_integral_cap(config["motor_2"][config_entry])
            if config_entry=="pid_integral_gain":
                self.motor_2.set_pid_integral_gain(config["motor_2"][config_entry])
            if config_entry=="pid_proportional_gain":
                self.motor_2.set_pid_proportional_gain(config["motor_2"][config_entry])
            if config_entry=="sensor_type_select":
                print("self.motor_2.set_sensor_type_select(18)")
                self.motor_2.set_sensor_type_select(18)
                #self.motor_2.set_sensor_type_select(config["motor_2"][config_entry][0])
            if config_entry=="stall_detection":
                self.motor_2.set_stall_detection(config["motor_2"][config_entry])
        if save:
            self.save_configuration_in_eeprom()
        self.emergency_stop_release()

    ##############################################
    #    CLASS INTERNALS                         #
    ##############################################

    def get_device_id_list(self):
        matching_serial_device_paths = []
        for serial_device_path_pattern in self.serial_device_path_patterns:
            matching_serial_device_paths.extend(glob.glob(serial_device_path_pattern))
        return matching_serial_device_paths

    def _get_bit_(self, number, place):
        return (number & (1 << place)) >> place

    def add_to_queue(
            self, 
            serial_command, 
            event=None,
            callback=None):
        if event is not None:
            event.clear()
        self.queue.put((serial_command, event, callback))

    def get_serial_response(self):
        try:
            response_char = " "
            response_str = ""
            while ord(response_char) != 13:
                response_char = self.serial.read(1)
                response_str += response_char.decode('utf-8')
            response_str = response_str[:-1] # trim /r from end
            #print("----->13 response_str",response_str)
            command_response_l = response_str.split('=')
            return True, command_response_l
        except TypeError as te:
            #print("----->14",te)
            return False, ""
        except UnicodeDecodeError as ude:
            #print("----->15",ude)
            return False, ""

    def clear_remote_serial_buffer(self):
        command_success = True
        while command_success:
            command_success, command_response_l = self.get_serial_response()

    def get_command_echo(self):
        command_success, command_response_l = self.get_serial_response()
        if not command_success:
            if self.device_connected == True:
                self.status_receiver("event_controller_connected", False)
                self.device_connected = False
            self.status_receiver("motor_controller_unresponsive", False)
            return False, command_response_l
        # the response should be in ["+","-"]
        if len(command_response_l[0])>1: #if this is the wrong phase of the request
            return True, command_response_l
        if command_response_l[0]=="-":
            self.status_receiver("nak response for command", command_response_l)
            return False, command_response_l
        if command_response_l[0]=="+":
            return True, command_response_l

    def get_command_response(self):
        command_success, command_response_l = self.get_serial_response()
        if command_response_l=="":
            self.clear_remote_serial_buffer()
            return False, ""
        if not command_success:
            if self.device_connected == True:
                self.status_receiver("event_controller_connected", False)
                self.device_connected = False
            self.status_receiver("motor_controller_unresponsive", False)
            return False, command_response_l
        # the response should be in ["+","-"]
        if len(command_response_l)==2: #if this is the wrong phase of the request
            return True, command_response_l[1]
        if len(command_response_l)==1:
            if command_response_l[0]=="+":
                return True, command_response_l
            if command_response_l[0]=="-":
                self.status_receiver("nak response for command", command_response_l)
                self.clear_remote_serial_buffer()
                return False, command_response_l
        self.status_receiver("unexpected command response", command_response_l)
        self.clear_remote_serial_buffer()
        return False, ""

    def run(self):
        while True:
            #print("----->-1",self.device_connected, self.queue.qsize())
            serial_command, event, callback = self.queue.get(block=True, timeout=None)
            #print("----->0", serial_command, event, callback)
            self.serial.write(str.encode(serial_command +'\r'))
            command_echo = self.get_command_echo()
            #print("----->1", command_echo)
            if command_echo == ['\x00Starting ...']:
                #print("----->2.5")
                if callback is not None:
                    #print("----->10")
                    callback(False, "", event)
                else:
                    continue
            try:
                command_success = command_echo[0]
                #print("----->3", command_success)
                command_response_l = command_echo[1]
                #print("----->4", command_response_l)
            except TypeError as te:
                if callback is not None:
                    #print("----->10")
                    callback(False, "", event)
                else:
                    continue
            if command_success:
                #print("----->5")
                command_success, command_response_l = self.get_command_response()
                #print("----->6", command_success, command_response_l)
                if command_success:
                    #print("----->7",self.device_connected)
                    if self.device_connected == False:
                        self.device_connected = True
                        self.status_receiver("event_controller_connected", True)
                    #print(command_response_l)
                    #self.status_receiver("command_response", command_response_l)
                    if callback is not None:
                        #print("----->8")
                        if command_response_l.startswith("Roboteq"):
                            if serial_command=="?FID":
                                callback(True, command_response_l, event)
                        else:
                            callback(True, command_response_l, event)
                else:
                    #print("----->9")
                    if callback is not None:
                        #print("----->10")
                        callback(False, "", event)
            else: 
                #print("----->11")
                self.clear_remote_serial_buffer()
                if callback is not None:
                    #print("----->12")
                    callback(False, "", event)


"""
def data_receiver_stub(msg):
    print("data_receiver_stub",msg)
def status_receiver_stub(msg,msg2=""):
    print("status_receiver_stub",msg,msg2 )
def exception_receiver_stub(msg):
    print("exception_receiver_stub",msg)
sdc = SDC(
    data_receiver_stub, 
    status_receiver_stub, 
    exception_receiver_stub,
    {}, #config
)
"""