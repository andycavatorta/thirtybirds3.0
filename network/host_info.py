#!/usr/bin/python
# -*- coding: ascii -*-

"""
Intended use:
This script sniffs and returns various network data about the host
"""

import threading

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions

@capture_exceptions.Class
class Host_Info(threading.Thread):
    def __init__(self, callback=None, test_interval=10):
        threading.Thread.__init__(self)
        self.callback = callback
        self.test_interval = test_interval


    def get_local_ip(self, interface_name):
        pass

    def start_testing(self):
        pass


    def stop_testing(self):
        pass


    def run(self):
        while True:

