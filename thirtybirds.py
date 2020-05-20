#!/usr/bin/python

"""
== fix before proceeding ==

simplify and unify data types used in network system  [ json | str | byte | etc]

why does reconnection sometimes fail?

in thirtybirds_connection, unify connection status reported by discovery and detect_disconnect

make receivers thread safe

make detect_disconnect thread safe

daemonize all threada
    why does that cause the script to end?  

this script and scripts called here should return a reference to the calling app.  
    for use with interactive shell

add logging option with native logging module
    because log rotation and size limits

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
        capture_exceptions.init(self.exception_receiver)
        self.app_settings = app_settings
        self.app_path = app_path
        self.network_message__callback = network_message__callback
        self.exception_callback = exception_callback
        self.network_status_change_callback = network_status_change_callback

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

        self.tb_connection = thirtybirds_connection.Thirtybirds_Connection(
            self.hostinfo.get_local_ip(),
            hostname = self.hostname,
            controller_hostname = settings.Network.controller_hostname,
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

















"""

@capture_exceptions.Function
def exception_receiver(msg):
    print("exception_receiver",msg)

# start reporting
capture_exceptions.init(exception_receiver)

@capture_exceptions.Function
def network_status_change_receiver(online_status):
    pass
    #print("online_status",online_status)

@capture_exceptions.Function
def network_message_receiver(topic, message):
    print("network_message_receiver",topic, message)

@capture_exceptions.Function
def collate(base_settings_module, optional_settings_module):
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

@capture_exceptions.Function
def init(app_settings,app_path):

    hostinfo = host_info.Host_Info(
        online_status_change_receiver=network_status_change_receiver, 
        exception_receiver = exception_receiver)
    
    # run updates on app and tb 

    #################################
    # c o l a t e   s e t t i n g s #
    #################################
    
    collate(settings, app_settings)
    
    status_type_names = [i for i in dir(settings.Reporting.Status_Types) if not (i[:2]=="__" and i[-2:]=="__")] 
    
    #########################
    # a p p l y   f l a g s #
    #########################
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
        hostname = sys.argv[sys.argv.index("-hostname")+1]
    except ValueError as e:
        hostname = hostinfo.get_hostname()
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

    for status_type_name in status_type_names:
        try:
            capture_or_ignore = sys.argv[sys.argv.index("-{0}".format(status_type_name))+1]
            setattr(settings.Reporting.Status_Types, status_type_name, True if update_on_start == "true" else False)
        except ValueError as e:
            pass
        except IndexError as e:
            print("usage: python ____.py -{0} [capture|ignore]".format(status_type_name))
            sys.exit(0)

    ##############################################
    # s t a r t   s t a t u s    r e c e i v e r #
    ##############################################

    status_recvr = Status_Receiver(True)

    for status_type_name in status_type_names:
        capture_or_ignore = getattr(settings.Reporting.Status_Types, status_type_name)
        if capture_or_ignore:
            status_recvr.activate_capture_type(status_type_name)
        else:
            status_recvr.deactivate_capture_type(status_type_name)
    
    #############################
    # s t a r t   n e t w o r k #
    #############################
    
    tb_connection = thirtybirds_connection.Thirtybirds_Connection(
        hostinfo.get_local_ip(),
        hostname = hostname,
        controller_hostname = settings.Network.controller_hostname,
        discovery_multicast_group = settings.Network.discovery_multicast_group,
        discovery_multicast_port = settings.Network.discovery_multicast_port,
        discovery_response_port = settings.Network.discovery_response_port,
        pubsub_pub_port = settings.Network.pubsub_publish_port,
        network_message_receiver = network_message_receiver,
        exception_receiver = exception_receiver,
        status_receiver = status_recvr,
        heartbeat_interval = settings.Network.heartbeat_interval,
        heartbeat_timeout_factor = settings.Network.heartbeat_timeout_factor,
        caller_interval = settings.Network.caller_interval
    )
    
    ###################################################
    # s t a r t   h o s t - s p e c i f i c   c o d e #
    ###################################################

"""



