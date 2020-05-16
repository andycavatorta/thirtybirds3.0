#!/usr/bin/python
# -*- coding: ascii -*-

"""
Intended use:
This script creates and manages the conneciton between thirtybirds clients and their controller
"""

import os
import sys
import time

from . import discovery
from . import Network_Defaults

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions
from . import pub_sub

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
        self.controller_ip = ""
        self.discovery_multicast_group = discovery_multicast_group
        self.discovery_multicast_port = discovery_multicast_port
        self.discovery_response_port = discovery_response_port
        self.pubsub_pub_port = pubsub_pub_port
        self.pubsub_pub_port2 = pubsub_pub_port2
        self.exception_receiver = exception_receiver
        self.role = Network_Defaults.DISCOVERY_ROLE_RESPONDER if hostname == controller_hostname else Network_Defaults.DISCOVERY_ROLE_CALLER

        self.discovery = discovery.Discovery(
            ip_address = ip_address,
            hostname = hostname,
            controller_hostname = controller_hostname,
            discovery_multicast_group = discovery_multicast_group,
            discovery_multicast_port = discovery_multicast_port,
            discovery_response_port = discovery_response_port,
            caller_period = 5,
            discovery_update_receiver = self.discovery_update_receiver,
            exception_receiver = exception_receiver)

        self.pub_sub = pub_sub.Pub_Sub(
            hostname = self.hostname,
            local_ip = self.ip_address,
            publish_port = self.pubsub_pub_port,
            role = self.role,
            message_receiver = self.subscription_message_receiver,
            exception_receiver = self.exception_receiver)

    def subscription_message_receiver(self, topic, message):
        print("subscription_message_receiver",topic, message)

    def discovery_update_receiver(self,message):
        print("discovery_update_receiver",message, self.role)
        if self.role == Network_Defaults.DISCOVERY_ROLE_CALLER:
            print("discovery_update_receiver 1",message)
            if message["status"] == Network_Defaults.DISCOVERY_STATUS_FOUND:
                print("discovery_update_receiver 2",message)
                if message["hostname"] == self.controller_hostname:
                    print("discovery_update_receiver 3",message)
                    self.controller_ip = message["ip"]
                    self.discovery.end_caller()
                    self.pub_sub.connect_to_publisher(
                        self.controller_hostname, 
                        self.controller_ip, 
                        self.pubsub_pub_port)
                    print("discovery_update_receiver ",message)
                else:
                    print("Wrong controller found?", message["hostname"])
        
        if self.role == Network_Defaults.DISCOVERY_ROLE_RESPONDER:
            print("discovery_update_receiver 4",message)
            if message["status"] == Network_Defaults.DISCOVERY_STATUS_FOUND:
                print("discovery_update_receiver 5",message)




