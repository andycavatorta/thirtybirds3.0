#!/usr/bin/python
# -*- coding: ascii -*-

"""
Intended use:
This script can receive a pub-sub socket and detects if an automatic 
periodic message does not arrive before a threshold period.
It can also generate such periodic messages for other hosts to receive.
The detection of disconnections can be useful for automatic reconnection.
"""

import threading
import time

class Publisher(): # this could probably be done with a generator rather than a class.
    def __init__(
            self, 
            publisher_hostname, 
            timeout, 
            status_receiver,
            unsubscribe
        ):
        self.timeout = timeout
        self.publisher_hostname = publisher_hostname
        self.status_receiver = status_receiver
        self.last_heartbeat = 0
        self.disconnected = True 
        self.unsubscribe = unsubscribe

    def check_for_timeout(self):
        _disconnected_ = False if time.time() - self.timeout < self.last_heartbeat else True
        print("check_for_timeout", self.publisher_hostname, _disconnected_, self.disconnected, time.time() - self.timeout, self.last_heartbeat)
        if self.disconnected != _disconnected_:
            self.disconnected = _disconnected_
            self.status_receiver(self.publisher_hostname, _disconnected_)
            self.unsubscribe(self.publisher_hostname)

    def record_heartbeat(self):
        self.last_heartbeat = time.time()

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

class Detect_Disconnect(threading.Thread):
    def __init__(
        self, 
        hostname,
        pub_sub,
        heartbeat_timeout_factor,
        heartbeat_interval,
        status_receiver,
        exception_receiver
    ):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.pub_sub = pub_sub
        self.status_receiver = status_receiver
        self.exception_receiver = exception_receiver
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_interval * heartbeat_timeout_factor
        self.topic = "__heartbeat__"
        self.publishers = {}
        self.send_periodic_heartbeats = Send_Periodic_Heartbeats(
            self.topic,
            self.pub_sub,
            self.hostname,
            self.heartbeat_interval
        )
        self.start()
        self.pub_sub.subscribe_to_topic(self.topic)

    def subscribe(self, publisher_hostname):
        # NOT_THREAD_SAFE
        self.publishers[publisher_hostname] = Publisher(
            publisher_hostname, 
            self.heartbeat_timeout,
            self.status_receiver,
            self.unsubscribe
        )

    def unsubscribe(self, publisher_hostname):
        # NOT_THREAD_SAFE
        del self.publishers[publisher_hostname]

    def record_heartbeat(self, publisher_hostname):
        # NOT_THREAD_SAFE
        publisher_hostname = publisher_hostname.decode("utf-8") 
        if publisher_hostname not in self.publishers:
            self.subscribe(publisher_hostname)
        self.publishers[publisher_hostname].record_heartbeat()

    def run(self):
        while True: 
            for publisher_hostname,val in self.publishers.items():
                val.check_for_timeout() 
            time.sleep(self.heartbeat_interval)



