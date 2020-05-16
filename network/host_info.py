#!/usr/bin/python
# -*- coding: ascii -*-

"""
Intended use:
This script sniffs and returns various network data about the host
"""

import netifaces
import os
import queue
import requests
import socket
import sys
import time
import threading

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions

@capture_exceptions.Class
class Host_Info(threading.Thread):
    def __init__(self, online_status_change_receiver=None, exception_receiver=None, test_interval=10):
        threading.Thread.__init__(self)
        self.online_status_change_receiver = online_status_change_receiver
        self.exception_receiver = exception_receiver
        capture_exceptions.init(self.exception_receiver)
        self.test_interval = test_interval
        self.queue = queue.Queue()
        self.online_status = False
        if self.online_status_change_receiver:
            self.start()

    def get_hostname(self):
        try:
            return socket.gethostname()
        except Exception:
            return False

    def get_interface_names(self):
        return netifaces.interfaces()

    def get_local_ip(self, specified_interface_name=None):
        interface_names = netifaces.interfaces()
        if specified_interface_name in interface_names:
            return netifaces.ifaddresses(specified_interface_name)[netifaces.AF_INET][0]['addr']
        for iface in interface_names:
            try:
                ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
                if ip[0:3] != "127":
                    return ip
            except Exception as e:
                pass
        return False

    def get_global_ip(self):
        try:
            return requests.get('http://ip.42.pl/raw').text
        except Exception as e:
            return False

    def get_online_status(self):
        r = self.get_local_ip()
        self.online_status = False if r==False else True
        return self.online_status

    def start_polling_online_status(self):
        self.queue.put(True)

    def stop_polling_online_status(self):
        self.queue.put(False)

    def run(self):
        polling = False
        while True:
            time.sleep(self.test_interval)
            try:
                polling = self.queue.get(False)
            except queue.Empty:
                pass

            if polling:
                if self.online_status != self.get_online_status():
                    self.online_status = not self.online_status
                    self.online_status_change_receiver(self.online_status)