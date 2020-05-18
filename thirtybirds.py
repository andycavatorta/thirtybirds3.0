"""
to do:
make comprehaneive reporting system
    report data to server
    select log level using conf and args
    create a system to dynamically change data collection at runtime
    make each receiver a single class passed into each module that can be modified globally using class variables?

make receivers thread safe

collate app and tb settings

add exception handling everywhere

make detect_disconnect thread safe

sumplify and unify data types used in network system  [ json | str | byte | etc]
    is protobuf better tha json?


"""

import os
import sys

tb_path = os.path.dirname(os.path.realpath(__file__))

from .network import host_info
from .network import thirtybirds_connection
from .reporting.exceptions import capture_exceptions
from . import settings as tb_settings

@capture_exceptions.Function
def exception_receiver(msg):
    print("exception_receiver",msg)

# start reporting
capture_exceptions.init(exception_receiver)

@capture_exceptions.Function
def status_receiver(
    file_path,
    object_path,
    message,
    level,
    params):
    print("----------------")
    print(file_path)
    print(object_path)
    print(message)
    print(level)
    for name, val in params.items():
        print("  ", name, ":", val)

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
    print("  -forceupdate")
    print("    run all version updates specified in settings")

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
        print("usage: python3 ____.py --hostname $hostname")
        sys.exit(0)

    try:
        sys.argv.index("-forceupdate")
        forceupdate = True
    except ValueError as e:
        forceupdate = False
    
    # run updates on app and tb if specified

    #################################
    # c o l a t e   s e t t i n g s #
    #################################
    
    collate(tb_settings, app_settings)

    #############################
    # s t a r t   n e t w o r k #
    #############################
    
    #print(hostname, forceupdate)
    
    #print(app_settings.Network.controller_hostname)
    
    tb_connection = thirtybirds_connection.Thirtybirds_Connection(
        hostinfo.get_local_ip(),
        hostname = hostname,
        controller_hostname = tb_settings.Network.controller_hostname,
        discovery_multicast_group = tb_settings.Network.discovery_multicast_group,
        discovery_multicast_port = tb_settings.Network.discovery_multicast_port,
        discovery_response_port = tb_settings.Network.discovery_response_port,
        pubsub_pub_port = tb_settings.Network.pubsub_publish_port,
        exception_receiver = exception_receiver,
        status_receiver = status_receiver,
        heartbeat_interval = tb_settings.Network.heartbeat_interval,
        heartbeat_timeout_factor = tb_settings.Network.heartbeat_timeout_factor,
        caller_interval = tb_settings.Network.caller_interval
    )
    
    # start host-specific code




