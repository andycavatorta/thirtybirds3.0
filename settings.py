"""
This file contains the default config data for the reports system

On start-up thirtybirds loads config data.  It loads default configs from config/ unless otherwise specified.  New config data can be loaded dynamically at runtime.

Typical usage example:

from config import reports

foo = ClassFoo(reports.foo_config)

"""

class Network():
    discovery_method = "multicast"
    discovery_multicast_group = "224.3.29.71"
    discovery_multicast_port = 10020
    discovery_response_port = 10021
    pubsub_publish_port = 10022
    heartbeat_interval = 5
    heartbeat_timeout_factor = 1.5
    caller_interval = 5

class Reporting():
    app_name = "thirtybirds"
    #logfile_location = "logs/thirtybirds.log"
    #level = "ERROR" #[DEBUG | INFO | WARNING | ERROR | CRITICAL]
    print_to_stdout = True
    publish_as_topic = "thirtybirds_exception"

    publish_to_dash = True

    class Status_Types:
        EXCEPTIONS = True
        INITIALIZATIONS = True
        NETWORK_CONNECTIONS = True
        NETWORK_MESSAGES = True
        SYSTEM_STATUS = True
        VERSION_STATUS = True
        ADAPTER_STATUS = True

class Update_Thirtybirds():
    repo_owner = "andycavatorta"
    repo_name = "thirtybirds_3"
    branch = "master"


