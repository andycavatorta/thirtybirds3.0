#!/usr/bin/python

"""
== fix before proceeding ==

in thirtybirds_connection, unify connection status reported by discovery and detect_disconnect

make receivers thread safe

make detect_disconnect thread safe

daemonize all threada
    why does that cause the script to end?  

add logging option with native logging module
    because log rotation and size limits

try using relative imports within tb instead of sys paths

== future features ==

management interface s
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
import os
import sys

tb_path = os.path.dirname(os.path.realpath(__file__))

from .network import host_info
from .network import thirtybirds_connection
from .reporting.exceptions import capture_exceptions
from .reporting.status.status_receiver import Status_Receiver 
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

        capture_exceptions.init(self.exception_receiver)

        self.hostinfo = host_info.Host_Info(
            online_status_change_receiver=self.network_status_change_receiver, 
            exception_receiver = self.exception_receiver)

        self.hostname = self.hostinfo.get_hostname()

        self.collate_settings(settings, app_settings)
        
        self.status_type_names = [i for i in dir(settings.Reporting.Status_Types) if not (i[:2]=="__" and i[-2:]=="__")] 
    
        self.apply_flags()

        self.status_recvr = Status_Receiver(True)

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

    def exception_receiver(self, exception):
        # to do : add logging, if in config
        # if client, publish exceptions to controller
        # optional callback, though I don't know when it could be useful
        print("exception_receiver",exception)
        try:
            self.exception_callback(exception)
        except TypeError:
            pass

    def network_status_change_receiver(self, online_status):
        # todo: log loss of network
        # report change back to app.  it might be important to halt hardware
        print("network_status_change_receiver",online_status)
        try:
            self.exception_callback(exception)
        except TypeError:
            pass

    def network_message_receiver(self, topic, message):
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

