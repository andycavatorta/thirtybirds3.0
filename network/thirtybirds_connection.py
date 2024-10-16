#!/usr/bin/python

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
#from . import http_server #self-starting

@capture_exceptions.Class
class Thirtybirds_Connection():
    def __init__(
        self,
        ip_address,
        hostname,
        client_names,
        controller_hostname,
        discovery_multicast_group,
        discovery_multicast_port,
        discovery_response_port,
        pubsub_pub_port,
        network_message_receiver,
        exception_receiver,
        status_receiver,
        network_status_change_receiver,
        heartbeat_interval,
        heartbeat_timeout_factor,
        caller_interval):

        capture_exceptions.init(exception_receiver)
        self.ip_address = ip_address
        self.hostname = hostname
        self.client_names = client_names
        self.controller_hostname = controller_hostname
        self.controller_ip = ""
        self.discovery_multicast_group = discovery_multicast_group
        self.discovery_multicast_port = discovery_multicast_port
        self.discovery_response_port = discovery_response_port
        self.pubsub_pub_port = pubsub_pub_port
        self.network_message_receiver = network_message_receiver
        self.exception_receiver = exception_receiver
        self.status_receiver = status_receiver
        self.network_status_change_receiver = network_status_change_receiver
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout_factor = heartbeat_timeout_factor
        self.caller_interval = caller_interval
        self.role = Network_Defaults.DISCOVERY_ROLE_RESPONDER if hostname == controller_hostname else Network_Defaults.DISCOVERY_ROLE_CALLER
        self.status_receiver.collect("starting",self.status_receiver.types.INITIALIZATIONS)
        self.connections = {}
        if self.role == Network_Defaults.DISCOVERY_ROLE_RESPONDER:
            [self.connections.setdefault(x, False) for x in self.client_names] 
        else:
            self.connections[controller_hostname] = False

        self.pub_sub = pub_sub.Pub_Sub(
            hostname = self.hostname,
            local_ip = self.ip_address,
            publish_port = self.pubsub_pub_port,
            role = self.role,
            message_receiver = self.subscription_message_receiver,
            exception_receiver = self.exception_receiver,
            status_receiver = self.status_receiver)

        self.detect_disconnect = detect_disconnect.Detect_Disconnect(
            hostname = self.hostname,
            pub_sub = self.pub_sub,
            heartbeat_timeout_factor = self.heartbeat_timeout_factor,
            heartbeat_interval = self.heartbeat_interval,
            disconnect_event_receiver = self.disconnect_event_receiver,
            exception_receiver = self.exception_receiver,
            status_receiver = self.status_receiver)

        self.discovery = discovery.Discovery(
            ip_address = ip_address,
            hostname = hostname,
            controller_hostname = controller_hostname,
            discovery_multicast_group = discovery_multicast_group,
            discovery_multicast_port = discovery_multicast_port,
            discovery_response_port = discovery_response_port,
            caller_period = self.caller_interval,
            discovery_update_receiver = self.discovery_update_receiver,
            exception_receiver = exception_receiver,
            status_receiver = self.status_receiver)

        self.send = self.pub_sub.send
        self.subscribe_to_topic = self.pub_sub.subscribe_to_topic
        self.unsubscribe_from_topic = self.pub_sub.unsubscribe_from_topic

        self.status_receiver.collect("started",self.status_receiver.types.INITIALIZATIONS)

    def check_connections(self):
        all_connected = True
        for value in self.connections.values():
            if value == False:
                all_connected = False
        return (all_connected,self.connections)

    def disconnect_event_receiver(self, disconnected_hostname, disconnection_status):
        self.status_receiver.collect("disconnection",self.status_receiver.types.NETWORK_CONNECTIONS, {"disconnected_hostname":disconnected_hostname,"disconnection_status":disconnection_status})
        self.connections[disconnected_hostname] = not disconnection_status
        self.network_status_change_receiver(not disconnection_status, disconnected_hostname)
        if self.role == Network_Defaults.DISCOVERY_ROLE_CALLER:
            if disconnection_status == True:
                self.discovery.start_caller()

    def subscription_message_receiver(self, topic, message, origin, destination):
        # topics with dunder names are for internal TB use 
        if topic == b"__heartbeat__":
            self.detect_disconnect.record_heartbeat(message)
        else:
            self.network_message_receiver(topic, message, origin, destination)

    def discovery_update_receiver(self,message):
        # todo: cover the case of disconnections and unsubscriptions
        self.status_receiver.collect(
            "connection status update",
            self.status_receiver.types.NETWORK_CONNECTIONS, 
            {
                "hostname":message["hostname"],
                "status":message["status"],
                "ip":message["ip"]
            }
        )
        self.connections[message["hostname"]] = True
        if self.role == Network_Defaults.DISCOVERY_ROLE_CALLER:
            if message["status"] == Network_Defaults.DISCOVERY_STATUS_FOUND:
                if message["hostname"] == self.controller_hostname:
                    self.controller_ip = message["ip"]
                    self.discovery.end_caller()
                    self.pub_sub.connect_to_publisher(
                        self.controller_hostname, 
                        self.controller_ip, 
                        self.pubsub_pub_port)
                    self.detect_disconnect.subscribe(message["hostname"])
                else:
                    self.status_receiver.types.NETWORK_CONNECTIONS, 
                    {
                        "controller_hostname":message["hostname"],
                        "controller_status":message["status"],
                        "controller_ip":message["ip"]
                    }
        
        if self.role == Network_Defaults.DISCOVERY_ROLE_RESPONDER:
            if message["status"] == Network_Defaults.DISCOVERY_STATUS_FOUND:

                self.pub_sub.connect_to_publisher(
                    message["hostname"], 
                    message["ip"], 
                    self.pubsub_pub_port)
                self.detect_disconnect.subscribe(message["hostname"])
