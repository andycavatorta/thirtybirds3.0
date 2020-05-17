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
def status_receiver(msg):
    print("status_receiver",msg)

@capture_exceptions.Function
def network_status_change_receiver(online_status):
    print("online_status",online_status)

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
    


    #############################
    # s t a r t   n e t w o r k #
    #############################
    
    #print(hostname, forceupdate)
    
    #print(app_settings.Network.controller_hostname)

    tb_connection = thirtybirds_connection.Thirtybirds_Connection(
        hostinfo.get_local_ip(),
        hostname = hostname,
        controller_hostname = app_settings.Network.controller_hostname,
        discovery_multicast_group = tb_settings.Network.discovery_multicast_group,
        discovery_multicast_port = tb_settings.Network.discovery_multicast_port,
        discovery_response_port = tb_settings.Network.discovery_response_port,
        pubsub_pub_port = tb_settings.Network.pubsub_publish_port,
        exception_receiver = exception_receiver,
        heartbeat_interval = tb_settings.Network.heartbeat_interval,
        heartbeat_timeout_factor = tb_settings.Network.heartbeat_timeout_factor,
        caller_interval = tb_settings.Network.
    )

    
    # start host-specific code





"""
import os
import socket
import sys

from config import settings 
from config import utils as config_utils
from reports import reports
#from system import status
from network import connection
from updates import update as thirtybirds_update
from updates import update as app_update

THIRTYBIRDS_BASE_PATH = os.path.dirname(os.path.realpath(__file__))

try:
    HOSTNAME = sys.argv[sys.argv.index("-hostname")+1]
except ValueError as e:
    HOSTNAME = socket.gethostname()
except IndexError as e:
    print("usage: python3 ____.py --hostname $hostname")
    sys.exit(0)

try:
    LOGLEVEL = sys.argv[sys.argv.index("-loglevel")+1]
except ValueError as e:
    LOGLEVEL = "ERROR"
except IndexError as e:
    print("usage: python3 ____.py --loglevel $loglevel")
    sys.exit(0)

try:
    sys.argv.index("-forceupdate")
    FORCEUPDATE = True
except ValueError as e:
    FORCEUPDATE = False

def subscribed_message_handler(topic, message):
    print(topic, message)

def network_status_message_handler(message):
    print(message)

def init(app_settings, app_base_path):
    config_utils.collate(settings, app_settings)
    # overwrite log level
    # overwrite update_on_start for both the app and for tb
    # start network
    connection_instance = connection.init(
        hostname=HOSTNAME,
        role = getattr(settings.Roles, HOSTNAME),
        pubsub_pub_port = settings.Network.pubsub_publish_port, 
        discovery_method = settings.Network.discovery_method,
        discovery_multicast_group = settings.Network.discovery_multicast_group,
        discovery_multicast_port = settings.Network.discovery_multicast_port,
        discovery_response_port = settings.Network.discovery_response_port,
        message_callback = subscribed_message_handler, 
        status_callback = network_status_message_handler, 
        heartbeat_interval = settings.Network.heartbeat_interval,
        reporting_paramaters = settings.Reporting
        )
            

    return {
        "hostname":HOSTNAME,
        "network":connection_instance,
        }
"""