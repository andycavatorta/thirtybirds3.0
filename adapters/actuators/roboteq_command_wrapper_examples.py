
import queue
import threading

import roboteq_command_wrapper

config = {
    "boards":{
        "300:1058:3014688:1429493507:540422710":{},
        "300:1058:2031663:1429493506:540422710":{},
    },
    "motors":{
        "pitch_slider":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "channel":"1",
        },
        "bow_position_slider":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "channel":"2",
        }
    }
}

class Status_Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()

    def add_to_queue(self, name, value):
        self.queue.put((name, value))

    def run(self):
        while True:
            name, value = self.queue.get(True)
            print("status",name, value)

status_receiver = Status_Receiver()
status_receiver.start()

class Data_Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()

    def add_to_queue(self, message):
        self.queue.put(message)

    def run(self):
        while True:
            message = self.queue.get(True)
            print("data",message)

data_receiver = Data_Receiver()
data_receiver.start()

class Exception_Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()

    def add_to_queue(self, *args):
        print(1, args)
        self.queue.put(args)

    def run(self):
        while True:
            message = self.queue.get(True)
            print("exception",message)

exception_receiver = Exception_Receiver()
exception_receiver.start()

controllers = roboteq_command_wrapper.init(
    data_receiver.add_to_queue, 
    status_receiver.add_to_queue, 
    exception_receiver.add_to_queue, 
    config
)

