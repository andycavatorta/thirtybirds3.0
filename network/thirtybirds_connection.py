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
from . import detect_disconnect

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
        exception_receiver,
        heartbeat_interval,
        heartbeat_timeout_factor
        ):

        self.ip_address = ip_address
        self.hostname = hostname
        self.controller_hostname = controller_hostname
        self.controller_ip = ""
        self.discovery_multicast_group = discovery_multicast_group
        self.discovery_multicast_port = discovery_multicast_port
        self.discovery_response_port = discovery_response_port
        self.pubsub_pub_port = pubsub_pub_port
        self.exception_receiver = exception_receiver
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout_factor = heartbeat_timeout_factor
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

        self.detect_disconnect = detect_disconnect.Detect_Disconnect(
            hostname = self.hostname,
            pub_sub = self.pub_sub,
            heartbeat_timeout_factor = self.heartbeat_timeout_factor,
            heartbeat_interval = self.heartbeat_interval,
            status_receiver = self.disconnect_status_receiver,
            exception_receiver = self.exception_receiver)

    def disconnect_status_receiver(self, message):
        print("disconnect_status_receiver", message)

    def subscription_message_receiver(self, topic, message):
        print("subscription_message_receiver",topic, message)


    def discovery_update_receiver(self,message):
        if self.role == Network_Defaults.DISCOVERY_ROLE_CALLER:
            if message["status"] == Network_Defaults.DISCOVERY_STATUS_FOUND:
                if message["hostname"] == self.controller_hostname:
                    self.controller_ip = message["ip"]
                    self.discovery.end_caller()
                    self.pub_sub.connect_to_publisher(
                        self.controller_hostname, 
                        self.controller_ip, 
                        self.pubsub_pub_port)
                else:
                    print("Wrong controller found?", message["hostname"])
        
        if self.role == Network_Defaults.DISCOVERY_ROLE_RESPONDER:
            if message["status"] == Network_Defaults.DISCOVERY_STATUS_FOUND:
                self.pub_sub.connect_to_publisher(
                    self.controller_hostname, 
                    self.controller_ip, 
                    self.pubsub_pub_port)



