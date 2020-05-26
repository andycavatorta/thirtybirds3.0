#!/usr/bin/python

"""
== fix before proceeding ==

add version control

create command-line interface system
    can be extended by app
    systems:
        network
        version control
        os_and_hardware

have clients send exceptions and status messages to controller

daemonize all threada
    why does that cause the script to end?  

== future features ==

management interfaces
    web interface?
    interactive shell?
    log file that can be tailed

add authentication for raspberry pis
    authenticate on discover using certs?

send status and exceptions messages to controller

trim paths in status_receiver?

== future setup process ==

installers for Raspbian, Ubuntu, Windows, OSX

copyable disk images
    setup script:
        assign new hostname
        generate new ssh key

change password for pi
add thirtybirds user and run as that

"""
import copy
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import time

tb_path = os.path.dirname(os.path.realpath(__file__))

path_containing_tb_and_app = os.path.split(tb_path)[0]

from .network import host_info
from .network import thirtybirds_connection
from .version_control.software_management import Software_Management
from .reporting.exceptions import capture_exceptions
from .reporting.status.status_receiver import Status_Receiver 
from .reporting.hardware_management import Hardware_Management
from . import settings as tb_settings # this copy retains tb settings
from . import settings as settings # this copy gets collated with app settings

@capture_exceptions.Class
class Thirtybirds():
    def __init__(
            self,
            app_settings,
            app_path,
            network_message__callback=None,
            exception_callback=None,
            network_status_change_callback=None,
        ):
        self.app_settings = app_settings
        self.app_path = app_path
        self.network_message__callback = network_message__callback
        self.exception_callback = exception_callback
        self.network_status_change_callback = network_status_change_callback

    #def init(self):
        self.set_up_logging(self.app_path)

        capture_exceptions.init(self.exception_receiver)

        self.hostinfo = host_info.Host_Info(
            online_status_change_receiver=self.network_status_change_receiver, 
            exception_receiver = self.exception_receiver)

        self.hostname = self.hostinfo.get_hostname()

        self.collate_settings(settings, self.app_settings)
        
        self.status_type_names = [i for i in dir(settings.Reporting.Status_Types) if not (i[:2]=="__" and i[-2:]=="__")] 
    
        self.apply_flags()

        self.status_recvr = Status_Receiver(True, path_containing_tb_and_app, self.status_receiver)

        for status_type_name in self.status_type_names:
            capture_or_ignore = getattr(settings.Reporting.Status_Types, status_type_name)
            if capture_or_ignore:
                self.status_recvr.activate_capture_type(status_type_name)
            else:
                self.status_recvr.deactivate_capture_type(status_type_name)

        self.client_names = []
        for host,role in settings.Roles.hosts.items():
            if role == "controller":
                self.controller_hostname = host
            else:
                self.client_names.append(host)

        self.connection = thirtybirds_connection.Thirtybirds_Connection(
            self.hostinfo.get_local_ip(),
            hostname = self.hostname,
            controller_hostname = self.controller_hostname,
            client_names = self.client_names,
            discovery_multicast_group = settings.Network.discovery_multicast_group,
            discovery_multicast_port = settings.Network.discovery_multicast_port,
            discovery_response_port = settings.Network.discovery_response_port,
            pubsub_pub_port = settings.Network.pubsub_publish_port,
            network_message_receiver = self.network_message_receiver,
            exception_receiver = self.exception_receiver,
            status_receiver = self.status_recvr,
            heartbeat_interval = settings.Network.heartbeat_interval,
            heartbeat_timeout_factor = settings.Network.heartbeat_timeout_factor,
            caller_interval = settings.Network.caller_interval
        )
        self.connection.subscribe_to_topic("__status__")
        self.connection.subscribe_to_topic("__error__")

        # make two explicit instances of Software_Management
        self.tb_software_management = Software_Management(
            tb_path,
            self.exception_receiver,
            self.status_recvr
        )
        self.app_software_management = Software_Management(
            self.app_path,
            self.exception_receiver,
            self.status_recvr
        )
        os_version = self.tb_software_management.get_os_version()

        print(self.app_software_management.get_git_timestamp())
        print(self.app_software_management.pull_from_github())
        print(self.app_software_management.get_git_timestamp())

        self.hardware_management = Hardware_Management(os_version["name"])


    def set_up_logging(self, app_path):
        log_directory = "{0}/logs/".format(app_path)
        try:
            os.listdir(log_directory)
        except FileNotFoundError:
            os.mkdir(log_directory)
            open("{0}/__init__.py".format(log_directory), 'a').close()

        status_logging_path = "{0}/status.log".format(log_directory)
        self.status_logger = logging.getLogger("status")
        self.status_logger.setLevel(logging.DEBUG)
        status_handler = RotatingFileHandler(status_logging_path, maxBytes=100000,backupCount=20)
        self.status_logger.addHandler(status_handler)
        
        error_logging_path = "{0}/error.log".format(log_directory)
        self.error_logger = logging.getLogger("error")
        self.error_logger.setLevel(logging.DEBUG)
        error_handler = RotatingFileHandler(error_logging_path, maxBytes=100000,backupCount=20)
        self.error_logger.addHandler(error_handler)
        
    def apply_flags(self):
        try:
            sys.argv[sys.argv.index("-help")]
            print("thirtybirds command line options:")
            print("  -hostname $hostname")
            print("    run as specified $hostname")
            print("  -update_on_start [true|false]")
            print("    run all version updates specified in settings")
            for status_type_name in status_type_names:
                print("  -{0} [capture|ignore]".format(status_type_name))
                print("    capture or ignore status messages for {0}".format(status_type_name))
            sys.exit(0)
        except ValueError:
            pass

        try:
            self.hostname = sys.argv[sys.argv.index("-hostname")+1]
        except ValueError as e:
            pass
        except IndexError as e:
            print("usage: python ____.py -hostname $hostname")
            sys.exit(0)

        try:
            update_on_start = sys.argv[sys.argv.index("-update_on_start")+1]
            settings.Version_Control.update_on_start = True if update_on_start == "true" else False
        except ValueError as e:
            pass
        except IndexError as e:
            print("usage: python ____.py -update_on_start [true|false]")
            sys.exit(0)

        for status_type_name in self.status_type_names:
            try:
                capture_or_ignore = sys.argv[sys.argv.index("-{0}".format(status_type_name))+1]
                setattr(settings.Reporting.Status_Types, self.status_type_name, True if capture_or_ignore == "true" else False)
            except ValueError as e:
                pass
            except IndexError as e:
                print("usage: python ____.py -{0} [capture|ignore]".format(status_type_name))
                sys.exit(0)

    def status_receiver(self, status_details):
        status_details_str = "{},{},{},{}{},{}.{},{},{}".format(time.strftime("%Y-%m-%d %H:%M:%S", status_details["time_local"]), status_details["time_epoch"],status_details["hostname"],status_details["path"],status_details["script_name"], status_details["class_name"],status_details["method_name"],status_details["message"],status_details["args"])
        self.status_logger.error(status_details_str)
        if self.hostname != self.controller_hostname:
            try:
                self.connection.send("__status__", status_details_str)
            except AttributeError:
                pass

    def exception_receiver(self, exception):
        # to do : add logging, if in config
        # if client, publish exceptions to controller
        # optional callback, though I don't know when it could be useful
        #print("exception_receiver",exception)
        exception_details_str = "{0},{1},{2},{3}{4},{5}.{6},{7},{8},{9},{10},{11}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", exception["time_local"]), 
            exception["time_epoch"],
            exception["hostname"],
            exception["path"],
            exception["script_name"], 
            exception["class_name"],
            exception["method_name"],
            exception["args"],
            exception["kwargs"],
            exception["exception_type"],
            exception["exception_message"],
            exception["stacktrace"]
            )
        self.error_logger.error(exception_details_str)

        try:
            self.exception_callback(exception)
        except TypeError:
            pass

    def network_status_change_receiver(self, online_status):
        # todo: log loss of network
        # report change back to app.  it might be important to halt hardware
        print("network_status_change_receiver",online_status)
        try:
            self.network_status_change_callback(exception)
        except TypeError:
            pass

    def network_message_receiver(self, topic, message):
        if topic == "__status__":
            pass
            #log this    
        print("network_message_receiver",topic, message)
        try:
            self.network_message__callback(topic, message)
        except TypeError:
            pass

    def collate_settings(self, base_settings_module, optional_settings_module):
        base_settings_classnames = [i for i in dir(base_settings_module) if not (i[:2]=="__" and i[-2:]=="__")] 
        optional_settings_classnames = [i for i in dir(optional_settings_module) if not (i[:2]=="__" and i[-2:]=="__")]
        for optional_settings_class in optional_settings_classnames:
            if optional_settings_class not in base_settings_classnames:
                setattr(base_settings_module, optional_settings_class, getattr(optional_settings_module, optional_settings_class))
            else:
                base_settings_class_ref = getattr(base_settings_module, optional_settings_class)
                optional_settings_class_ref = getattr(optional_settings_module, optional_settings_class)
                # todo: it would be more concise and idiomatic to do the following with multiple inheritance.  if possible.
                optional_settings_class_variable_names = [attr for attr in dir(optional_settings_class_ref) if not callable(getattr(optional_settings_class_ref, attr)) and not attr.startswith("__")]
                for optional_settings_class_variable_name in optional_settings_class_variable_names:
                    setattr(base_settings_class_ref, optional_settings_class_variable_name, getattr(optional_settings_class_ref, optional_settings_class_variable_name))
