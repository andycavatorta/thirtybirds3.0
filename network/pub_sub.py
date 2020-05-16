#!/usr/bin/python
# -*- coding: ascii -*-

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
from . import Network_Defaults

class Subscription():
    def __init__(self, hostname, remote_ip, remote_port):
        self.hostname = hostname
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.connected = False

class Send_Queue(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue.Queue()

    def add_to_queue(self, topic, msg):
        self.queue.put((topic, msg))

    def run(self):
        while True:
            try:
                topic, msg = self.queue.get(True)
                self.socket.send_string("%s %s" % (topic, msg))
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

class Receiver_Queue(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback
        self.queue = queue.Queue()

    def add_to_queue(self, topic, msg):
        self.queue.put((topic, msg))

    def run(self):
        while True:
            try:
                topic, msg = self.queue.get(True)
                self.callback(topic, msg)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

class Pub_Sub(threading.Thread):
    def __init__(
            self, 
            hostname,
            local_ip, 
            publish_port,
            role,
            message_receiver,
            exception_receiver
        ):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.local_ip = local_ip
        self.publish_port = publish_port
        self.role = role
        self.message_receiver = message_receiver
        self.exception_receiver = exception_receiver
        self.subscriptions = {}

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

    def connect_to_publisher(self, hostname, remote_ip, remote_port):
        if hostname not in self.subscriptions:
            self.subscriptions[hostname] = Subscription(hostname, remote_ip, remote_port)
            self.sub_socket.connect("tcp://%s:%s" % (remote_ip, remote_port))

    def subscribe_to_topic(self, topic):
        # NOT_THREAD_SAFE
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, topic, encoding='utf-8')

    def unsubscribe_from_topic(self, topic):
        topic = topic.decode('ascii')
        # NOT_THREAD_SAFE
        self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, topic)

    def send(self, topic, msg):
        # NOT_THREAD_SAFE
        self.send_queue.add_to_queue(topic, msg)

    def run(self):
        while True:
            incoming = self.sub_socket.recv()
            topic, msg = incoming.split(' ', 1)
            self.receiver_queue.add_to_queue(topic, msg)

