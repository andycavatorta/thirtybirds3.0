#!/usr/bin/python

"""
Intended use:
This script can receive a pub-sub socket and detects if an automatic 
periodic message does not arrive before a threshold period.
It can also generate such periodic messages for other hosts to receive.
The detection of disconnections can be useful for automatic reconnection.
"""


import os
import sys
import threading
import time

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions

#@capture_exceptions.Class
class Publisher(): # this could probably be done with a generator rather than a class.
    def __init__(
            self, 
            publisher_hostname, 
            timeout, 
            disconnect_event_receiver,
            unsubscribe
        ):
        self.timeout = timeout
        self.publisher_hostname = publisher_hostname
        self.disconnect_event_receiver = disconnect_event_receiver
        self.last_heartbeat = 0
        self.disconnected = True 
        self.unsubscribe = unsubscribe

    def check_for_timeout(self):
        _disconnected_ = False if time.time() - self.timeout < self.last_heartbeat else True
        if self.disconnected != _disconnected_:
            self.disconnected = _disconnected_
            self.disconnect_event_receiver(self.publisher_hostname, _disconnected_)
            if _disconnected_ == True:
                self.unsubscribe(self.publisher_hostname)

    def record_heartbeat(self):
        self.last_heartbeat = time.time()

#@capture_exceptions.Class
class Send_Periodic_Heartbeats(threading.Thread):
    def __init__(
        self, 
        topic,
        pub_sub,
        local_hostname,
        heartbeat_interval
    ):
        threading.Thread.__init__(self)
        self.topic = topic
        self.pub_sub = pub_sub
        self.local_hostname = local_hostname
        self.heartbeat_interval = heartbeat_interval
        self.start()

    def run(self):
        while True: 
            self.pub_sub.send(self.topic, self.local_hostname)
            time.sleep(self.heartbeat_interval)

#@capture_exceptions.Class
class Detect_Disconnect(threading.Thread):
    def __init__(
        self, 
        hostname,
        pub_sub,
        heartbeat_timeout_factor,
        heartbeat_interval,
        disconnect_event_receiver,
        exception_receiver,
        status_receiver
    ):
        capture_exceptions.init(exception_receiver)
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.pub_sub = pub_sub
        self.disconnect_event_receiver = disconnect_event_receiver
        self.exception_receiver = exception_receiver
        self.status_receiver = status_receiver
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_interval * heartbeat_timeout_factor
        self.topic = "__heartbeat__"
        self.publishers = {}

        self.lock = threading.Lock()
        self.status_receiver.collect("starting",self.status_receiver.types.INITIALIZATIONS)
        self.send_periodic_heartbeats = Send_Periodic_Heartbeats(
            self.topic,
            self.pub_sub,
            self.hostname,
            self.heartbeat_interval
        )
        self.start()
        self.pub_sub.subscribe_to_topic(self.topic)
        self.status_receiver.collect("started",self.status_receiver.types.INITIALIZATIONS)

    def subscribe(self, publisher_hostname):
        # NOT_THREAD_SAFE
        self.lock .acquire()
        self.publishers[publisher_hostname] = Publisher(
            publisher_hostname, 
            self.heartbeat_timeout,
            self.disconnect_event_receiver,
            self.unsubscribe
        )
        self.lock .release()

    def unsubscribe(self, publisher_hostname):
        # NOT_THREAD_SAFE
        self.lock .acquire()
        del self.publishers[publisher_hostname]
        self.lock .release()

    def record_heartbeat(self, publisher_hostname):
        # NOT_THREAD_SAFE
        self.lock .acquire()
        publisher_hostnames = list(self.publishers.keys())
        self.lock .release()
        #if publisher_hostname not in self.publishers:
        if publisher_hostname not in publisher_hostnames:
            self.subscribe(publisher_hostname)
        self.publishers[publisher_hostname].record_heartbeat()

    def run(self):
        while True: 
            publisher_keys = list(self.publishers.keys())
            for publisher_key in publisher_keys:
                try:
                    self.publishers[publisher_key].check_for_timeout()
                except KeyError:
                    pass
            time.sleep(self.heartbeat_interval)
