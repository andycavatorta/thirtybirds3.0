import os
import sys

tb_path = os.path.dirname(os.path.realpath(__file__))

from .network import host_info
from .network import thirtybirds_connection
from .reporting.exceptions import capture_exceptions

def handle_exceptions(msg):
    print("handle_exceptions",handle_exceptions)

# start reporting
capture_exceptions.init(handle_exceptions)

@capture_exceptions.Function
def handle_online_status_change(online_status):
    print("online_status",online_status)

@capture_exceptions.Class
def init(app_settings,app_path):
    print("thirtybirds command like options:")
    print("  -hostname $hostname")
    print("    run as specified $hostname")
    print("  -forceupdate")
    print("    run all version updates specified in settings")

    hostinfo = host_info.Host_Info(handle_online_status_change)

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

    #############################
    # s t a r t   n e t w o r k #
    #############################
    
    print(hostname, forceupdate)
    
    print(app_settings.Network.controller_hostname)
    
    thirtybirds_connection.init(
        hostinfo.get_local_ip(),
        hostname = hostname,
        controller_hostname = app_settings.Network.controller_hostname,
        discovery_multicastGroup = app_settings.Network.discovery_multicastGroup,
        discovery_multicastPort = app_settings.Network.discovery_multicastPort,
        discovery_responsePort = app_settings.Network.discovery_responsePort,
        pubsub_pubPort = app_settings.Network.pubsub_pubPort,
        pubsub_pubPort2 = app_settings.Network.pubsub_pubPort2
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