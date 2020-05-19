#!/usr/bin/python

from status_receiver import Status_Receiver

status_recvr = Status_Receiver(True)
status_recvr.activate_capture_type("test_event")

class C():
    def a(self, x, y, z):
        status_recvr.collect("hello problems", "test_event", {"x":x, "y":y})

c = C()
c.a(1,2,3)


def a(x, y, z):
    status_recvr.collect("hello problems", "test_event", {"x":x, "y":y})

#a(1,2,3)
