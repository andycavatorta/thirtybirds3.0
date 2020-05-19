#!/usr/bin/python

"""

This module contains a single function that gathers info about the local where the function is run.

Its originaly written as a simple way provide context info for status messages.

"""

import inspect
import os
import socket 
import time

def get_context(class_ref = False):
    return {
        "time_epoch":time.time(),
        "time_local":time.localtime(),
        "hostname":socket.gethostname(),
        "path":os.getcwd(),
        "script_name":__file__,
        "class_name":class_ref.__class__.__name__ if class_ref else "",
        "method_name":inspect.stack()[0][3],
    }
