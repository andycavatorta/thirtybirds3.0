#!/usr/bin/python

"""
Intended use:
This script returns bi-directional pub-sub sockets between two hosts.

"""
import json
import os
import queue
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

@capture_exceptions.Class
class Subscription():
    def __init__(self, hostname, remote_ip, remote_port):
        self.hostname = hostname
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.connected = False

@capture_exceptions.Class
class Send_Queue(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue.Queue()

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            topic, message = self.queue.get(True)
            message_json = json.dumps(message)
            self.socket.send_string("%s %s" % (topic, message_json))

@capture_exceptions.Class
class Receiver_Queue(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback
        self.queue = queue.Queue()

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            topic, payload = self.queue.get(True)
            destination  = payload["destination"]
            if destination in ("", self.hostname)
                origin = payload["origin"]
                message = payload["message"]
                self.callback(topic, message, origin)

@capture_exceptions.Class
class Pub_Sub(threading.Thread):
    def __init__(
            self, 
            hostname,
            local_ip, 
            publish_port,
            role,
            message_receiver,
            exception_receiver,
            status_receiver
        ):
        capture_exceptions.init(exception_receiver)
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.local_ip = local_ip
        self.publish_port = publish_port
        self.role = role
        self.message_receiver = message_receiver
        self.exception_receiver = exception_receiver
        self.status_receiver = status_receiver
        self.subscriptions = {}

        self.status_receiver.collect("starting",self.status_receiver.types.INITIALIZATIONS)
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind("tcp://*:%s" % publish_port)
        self.sub_socket = self.context.socket(zmq.SUB)

        self.send_queue = Send_Queue(self.pub_socket)
        self.send_queue.daemon = True
        self.send_queue.start()

        self.receiver_queue = Receiver_Queue(self.message_receiver)
        self.receiver_queue.daemon = True
        self.receiver_queue.start()

        self.daemon = True
        self.start()
        self.status_receiver.collect("started",self.status_receiver.types.INITIALIZATIONS)

    def connect_to_publisher(self, hostname, remote_ip, remote_port):
        if hostname not in self.subscriptions:
            self.subscriptions[hostname] = Subscription(hostname, remote_ip, remote_port)
            self.sub_socket.connect("tcp://%s:%s" % (remote_ip, remote_port))

    def subscribe_to_topic(self, topic):
        # NOT_THREAD_SAFE
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, bytes(topic, 'utf-8'))

    def unsubscribe_from_topic(self, topic):
        # NOT_THREAD_SAFE
        self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, topic.decode('utf-8'))

    def send(self, topic, message, destination=""):
        payload = (
            "origin" = self.hostname,
            "destination" = destination,
            "message" = message
        )
        self.send_queue.add_to_queue(topic, payload)

    def run(self):
        while True:
            incoming = self.sub_socket.recv()
            topic, message_json = incoming.split(b' ', 1)
            self.receiver_queue.add_to_queue(topic, json.loads(message_json))

