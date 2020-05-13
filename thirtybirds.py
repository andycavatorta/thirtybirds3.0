import os
import sys

tb_path = os.path.dirname(os.path.realpath(__file__))

def init(app_settings,app_path):
    print("thirtybirds command like options:")
    print("  -hostname (hostname)")
    print("    run as specified hostname")
    print("  -forceupdate")
    print("    run all version updates specified in settings")

    print(sys.argv)
    print(tb_path)
    print(app_path)

    # apply settings and flags

    

    # start reporting



    # run updates on app and tb if specified



    # start network




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