#!/usr/bin/python

import inspect
import queue
import socket
import sys
import time
import threading

class Status_Receiver(threading.Thread):
    class types:
        pass
    capture_type_values = []
    def __init__(
        self, 
        print_to_stdout,
        callback=False
    ):
        threading.Thread.__init__(self)
        self.hostname = socket.gethostname()
        self.queue = queue.Queue()
        self.print_to_stdout = print_to_stdout,
        self.callback=callback
        self.start()
    
    def activate_capture_type(self, message_type):
        setattr(self.types, message_type, message_type)
        # NOT THREAD SAFE
        if message_type not in self.capture_type_values:
            self.capture_type_values.append(message_type)

    def deactivate_capture_type(self, message_type):
        setattr(self.types, message_type, message_type)
        # NOT THREAD SAFE
        try:
            self.capture_type_values.remove(message_type)
        except ValueError:
            pass

    def collect(self, message, message_type,  args={}, class_ref=""):
        if message_type in self.capture_type_values:
            caller_frame = inspect.stack()[1]
            fullpath = caller_frame.filename
            last_slash_position = fullpath.rfind("/")+1
            filename = fullpath[last_slash_position:]
            path = fullpath[:last_slash_position]
            try:
                class_name = caller_frame[0].f_locals["self"].__class__.__name__
            except KeyError:
                class_name = ""
            status_details = {
                "message":message,
                "time_epoch":time.time(),
                "hostname":self.hostname,
                "path":path,
                "script_name":filename,
                "class_name":class_name,
                "method_name":caller_frame.function,
                "args":args,
                "message_type":message_type,
            }
            self.queue.put(status_details)

    def run(self):
        while True:
            try:
                status_details = self.queue.get(True)
                if self.print_to_stdout:
                    print(
                        status_details["hostname"], 
                        status_details["path"], 
                        status_details["script_name"], 
                        status_details["class_name"], 
                        status_details["method_name"],
                        status_details["message"],
                        status_details["args"]
                    )
                    """
                    print("##### Status_Receiver #####")
                    print("message", ":", status_details["message"])
                    print("time_epoch", ":", status_details["time_epoch"])
                    print("hostname", ":", status_details["hostname"])
                    print("path", ":", status_details["path"])
                    print("script_name", ":", status_details["script_name"])
                    print("class_name", ":", status_details["class_name"])
                    print("method_name", ":", status_details["method_name"])
                    print("message_type", ":", status_details["message_type"])
                    print("args", ":", status_details["args"])
                    """
                if self.callback:
                    self.callback(status_details)
            except Exception as e:
                pass
