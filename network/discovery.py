#!/usr/bin/python

"""
Intended use:
Multiple hosts on a LAN can use this script to create a self-assembling network.

One host is configured as the server and listens for IP broadcast messages
on a specific IP and port.  

Other hosts are configured as clients which send broadcast messages containing 
the client hostname and IP on a specific IP and port.  
When the server receives a broadcast message from a client, it sends a 
return message containg the server hostname and IP.
Both client and server report the interaction to a discovery_update_receiver method that is passed 
into this module's init function.

This script may eventually support other methods such as connection brokers.
"""
import json
import os
import socket
import struct
import sys
import threading
import time
import yaml
import zmq

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions
from . import Network_Defaults

#####################
##### RESPONDER #####
#####################

@capture_exceptions.Class
class Responder(threading.Thread):
    def __init__(
            self, 
            hostname,
            local_ip, 
            discovery_multicast_group, 
            discovery_multicast_port, 
            discovery_response_port, 
            discovery_update_receiver,
            caller_period):
    
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.local_ip = local_ip
        self.discovery_multicast_port = discovery_multicast_port
        self.discovery_response_port = discovery_response_port
        self.discovery_update_receiver = discovery_update_receiver
        self.caller_period = caller_period

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((discovery_multicast_group, discovery_multicast_port))
        self.multicast_request = struct.pack("4sl", socket.inet_aton(discovery_multicast_group), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.multicast_request)
        #self.last_responese_by_ip = {}

    def response(self, remoteIP, msg_json): # response sends the local IP to the remote device
        #if remoteIP in self.last_responese_by_ip.keys():
        #    if self.last_responese_by_ip[remoteIP] + (self.caller_period * 2) > time.time():
        #        return
        #else:
        #    self.last_responese_by_ip[remoteIP] = time.time()
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.connect("tcp://%s:%s" % (remoteIP,self.discovery_response_port))
        socket.send(msg_json)
        socket.close()

    def run(self):
        while True:
            print("Responder")
            msg_json = self.sock.recv(1024)
            msg_d = yaml.safe_load(msg_json)
            remoteIP = msg_d["ip"]
            msg_d["status"] = "device_discovered"
            if self.discovery_update_receiver:
                resp_d = self.discovery_update_receiver(msg_d)
            resp_json = json.dumps({"ip":self.local_ip,"hostname":socket.gethostname()})
            resp_json = str.encode(resp_json)
            self.response(remoteIP,resp_json)

##################
##### CALLER #####
##################

@capture_exceptions.Class
class Caller_Send(threading.Thread):
    def __init__(self, local_hostname, local_ip, discovery_multicast_group, discovery_multicast_port, caller_period):
        threading.Thread.__init__(self)
        self.discovery_multicast_group = discovery_multicast_group
        self.discovery_multicast_port = discovery_multicast_port
        self.caller_period = caller_period
        self.multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        self.msg_d = {"ip":local_ip,"hostname":local_hostname}
        self.msg_json = json.dumps(self.msg_d)
        self.mcast_msg = bytes(self.msg_json, 'utf-8')
        self.active = True
        self.lock = threading.Lock()
    def set_active(self,val):
        self.lock .acquire()
        self.active = val
        self.lock .release()
    def run(self):
        while True:
            print("Caller_Send")
            self.lock .acquire()
            active = bool(self.active)
            self.lock .release()
            if active == True:
                self.multicast_socket.sendto(self.mcast_msg, (self.discovery_multicast_group, self.discovery_multicast_port))
            time.sleep(self.caller_period)

@capture_exceptions.Class
class Caller_Recv(threading.Thread):
    def __init__(self, recv_port, discovery_update_receiver, caller_send):
        threading.Thread.__init__(self)
        self.discovery_update_receiver = discovery_update_receiver
        self.caller_send = caller_send
        self.listen_context = zmq.Context()
        self.listen_sock = self.listen_context.socket(zmq.PAIR)
        self.listen_sock.bind("tcp://*:%d" % recv_port)
        self.msg = ""
        self.server_ip = ""
    def run(self):
        while True:
            print("Caller_Recv")
            msg_json = self.listen_sock.recv()
            msg_d = yaml.safe_load(msg_json)
            msg_d["status"] = "device_discovered"
            if self.discovery_update_receiver:
                self.discovery_update_receiver(msg_d)

###################
##### WRAPPER #####
###################

@capture_exceptions.Class
class Discovery():
    def __init__(
        self,
        ip_address,
        hostname,
        controller_hostname,
        discovery_multicast_group,
        discovery_multicast_port,
        discovery_response_port,
        caller_period,
        discovery_update_receiver,
        exception_receiver,
        status_receiver
    ):
        capture_exceptions.init(exception_receiver)
        self.ip_address = ip_address
        self.hostname = hostname
        self.controller_hostname = controller_hostname
        self.discovery_multicast_group = discovery_multicast_group
        self.discovery_multicast_port = discovery_multicast_port
        self.discovery_response_port = discovery_response_port
        self.caller_period = caller_period
        self.discovery_update_receiver = discovery_update_receiver
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.role = Network_Defaults.DISCOVERY_ROLE_RESPONDER if hostname == controller_hostname else Network_Defaults.DISCOVERY_ROLE_CALLER
        self.server_ip = ""
        self.status_receiver.collect("starting",self.status_receiver.types.INITIALIZATIONS)

        if self.role == Network_Defaults.DISCOVERY_ROLE_RESPONDER:
            self.responder = Responder(
                self.hostname,
                self.ip_address,
                self.discovery_multicast_group,
                self.discovery_multicast_port, 
                self.discovery_response_port,
                self.discovery_update_receiver,
                self.caller_period
            )
            self.responder.daemon = True
            self.responder.start()

        if self.role == Network_Defaults.DISCOVERY_ROLE_CALLER:
            self.caller_send = Caller_Send(
                self.hostname, 
                self.ip_address, 
                self.discovery_multicast_group, 
                self.discovery_multicast_port,
                self.caller_period
            )
            self.caller_recv = Caller_Recv(
                self.discovery_response_port, 
                self.discovery_update_receiver, 
                self.caller_send
            )
            self.caller_recv.daemon = True
            self.caller_send.daemon = True
            self.caller_recv.start()
            self.caller_send.start()
        self.status_receiver.collect("started",self.status_receiver.types.INITIALIZATIONS)

    def start_caller(self):
        if self.role == Network_Defaults.DISCOVERY_ROLE_CALLER:
            self.caller_send.set_active(True)

    def end_caller(self):
        if self.role == Network_Defaults.DISCOVERY_ROLE_CALLER:
            self.caller_send.set_active(False)
