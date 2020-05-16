#!/usr/bin/python
# -*- coding: ascii -*-

"""
Intended use:
This script creates and manages the conneciton between thirtybirds clients and their controller
"""

import os
import sys

from . import discovery
from . import Network_Defaults

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions




class Thirtybirds_Connection():
    def __init__(
        self,
        ip_address,
        hostname,
        controller_hostname,
        discovery_multicast_group,
        discovery_multicast_port,
        discovery_response_port,
        pubsub_pub_port,
        pubsub_pub_port2,
        exception_receiver
        ):

        self.ip_address = ip_address
        self.hostname = hostname
        self.controller_hostname = controller_hostname
        self.discovery_multicast_group = discovery_multicast_group
        self.discovery_multicast_port = discovery_multicast_port
        self.discovery_response_port = discovery_response_port
        self.pubsub_pub_port = pubsub_pub_port
        self.pubsub_pub_port2 = pubsub_pub_port2
        self.exception_receiver = exception_receiver

        self.discovery = discovery.Discovery(
            ip_address = ip_address,
            hostname = hostname,
            controller_hostname = controller_hostname,
            discovery_multicast_group = discovery_multicast_group,
            discovery_multicast_port = discovery_multicast_port,
            discovery_response_port = discovery_response_port,
            caller_period = 10,
            discovery_update_receiver = self.discovery_handler,
            exception_receiver = exception_receiver)

    def discovery_handler(self,message):
        print("discovery_handler",message)



