"""
to do:
make comprehaneive reporting system
    report data to server
    create a system to dynamically change data collection at runtime
    make each receiver a single class passed into each module that can be modified globally using class variables?

make receivers thread safe

add exception handling everywhere

make detect_disconnect thread safe

simplify and unify data types used in network system  [ json | str | byte | etc]
    is protobuf better tha json?

x select log level using conf and args

x collate app and tb settings

x make exception collector grab correct data
x      what is incorrect?

"""

import os
import sys

tb_path = os.path.dirname(os.path.realpath(__file__))

from .network import host_info
from .network import thirtybirds_connection
from .reporting.exceptions import capture_exceptions
from .reporting.status.status_receiver import Status_Receiver 
from . import settings as tb_settings

@capture_exceptions.Function
def exception_receiver(msg):
    print("exception_receiver",msg)

# start reporting
capture_exceptions.init(exception_receiver)


@capture_exceptions.Function
def network_status_change_receiver(online_status):
    print("online_status",online_status)

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

@capture_exceptions.Class
def init(app_settings,app_path):
    print("thirtybirds command like options:")
    print("  -hostname $hostname")
    print("    run as specified $hostname")
    print("  -update_on_start [true|false]")
    print("    run all version updates specified in settings")
    print("  -capture_exceptions [true|false]")
    print("    capture exceptions")
    print("  -capture_initializations [true|false]")
    print("    capture initializations")
    print("  -capture_network_connections [true|false]")
    print("    capture network connections")
    print("  -capture_network_messages [true|false]")
    print("    capture network messages")
    print("  -capture_system_status [true|false]")
    print("    capture system status")
    print("  -capture_version_status [true|false]")
    print("    capture version status")
    print("  -capture_adapter_status [true|false]")
    print("    capture adapter status")

    hostinfo = host_info.Host_Info(
        online_status_change_receiver=network_status_change_receiver, 
        exception_receiver = exception_receiver)

    #########################
    # a p p l y   f l a g s #
    #########################
    try:
        hostname = sys.argv[sys.argv.index("-hostname")+1]
    except ValueError as e:
        hostname = hostinfo.get_hostname()
    except IndexError as e:
        print("usage: python ____.py -hostname $hostname")
        sys.exit(0)

    try:
        update_on_start = sys.argv[sys.argv.index("-update_on_start")+1]
        app_settings.Version_Control.update_on_start = True if update_on_start == "true" else False
    except ValueError as e:
        pass
    except IndexError as e:
        print("usage: python ____.py -update_on_start [true|false]")
        sys.exit(0)

    reporting_parameters = [
        "capture_exceptions", 
        "capture_initializations", 
        "capture_network_connections", 
        "capture_network_messages", 
        "capture_system_status", 
        "capture_version_status", 
        "capture_adapter_status"
    ]

    for reporting_parameter in reporting_parameters:
        try:
             param_bool = sys.argv[sys.argv.index("-{0}".format(reporting_parameter))+1]
             setattr(app_settings.Reporting,reporting_parameter,True if param_bool == "true" else False)
        except ValueError as e:
            pass
        except IndexError as e:
            print("usage: python ____.py -{0} [true|false]".format(reporting_parameter))
            sys.exit(0)

    # run updates on app and tb if specified

    #################################
    # c o l a t e   s e t t i n g s #
    #################################
    
    collate(tb_settings, app_settings)

    ##############################################
    # s t a r t   s t a t u s    r e c e i v e r #
    ##############################################

    status_recvr = Status_Receiver(True)
    if tb_settings.Reporting.capture_initializations:
        status_recvr.activate_capture_type("initialization")
    if tb_settings.Reporting.capture_network_connections:
        status_recvr.activate_capture_type("network_connection")
    if tb_settings.Reporting.capture_network_messages:
        status_recvr.activate_capture_type("network_message")
    if tb_settings.Reporting.capture_system_status:
        status_recvr.activate_capture_type("system_status")
    if tb_settings.Reporting.capture_version_status:
        status_recvr.activate_capture_type("version_status")
    if tb_settings.Reporting.capture_adapter_status:
        status_recvr.activate_capture_type("adapter_status")

    #############################
    # s t a r t   n e t w o r k #
    #############################
    
    tb_connection = thirtybirds_connection.Thirtybirds_Connection(
        hostinfo.get_local_ip(),
        hostname = hostname,
        controller_hostname = tb_settings.Network.controller_hostname,
        discovery_multicast_group = tb_settings.Network.discovery_multicast_group,
        discovery_multicast_port = tb_settings.Network.discovery_multicast_port,
        discovery_response_port = tb_settings.Network.discovery_response_port,
        pubsub_pub_port = tb_settings.Network.pubsub_publish_port,
        exception_receiver = exception_receiver,
        status_receiver = status_recvr.collect,
        heartbeat_interval = tb_settings.Network.heartbeat_interval,
        heartbeat_timeout_factor = tb_settings.Network.heartbeat_timeout_factor,
        caller_interval = tb_settings.Network.caller_interval
    )
    
    # start host-specific code




