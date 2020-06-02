
import queue
import threading

import roboteq_macro_functions as roboteq

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
        },
        "bow_height":{
            "mcu_id":"300:1058: 3014688:1429493507:540422710",
            "channel":"1",
        },
        "bow_rotation":{
            "mcu_id":"300:1058:3014688:1429493507:540422710",
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

class Roboteq_Data_Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.start()

    def add_to_queue(self, message):
        self.queue.put(message)

    def run(self):
        while True:
            message = self.queue.get(True)
            print("data",message)
            if "internal_event" in message:
                do_tests()
                
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

controllers = roboteq.init(
    data_receiver.add_to_queue, 
    status_receiver.add_to_queue, 
    exception_receiver.add_to_queue, 
    config
)

def do_tests():
    for board_name in controllers.boards:
        controllers.boards[board_name].set_serial_data_watchdog(0)
    controllers.motors["pitch_slider"].go_to_speed_or_relative_position(200)
    controllers.motors["bow_position_slider"].go_to_speed_or_relative_position(200)
    controllers.motors["bow_height"].go_to_speed_or_relative_position(200)
    controllers.motors["bow_rotation"].go_to_speed_or_relative_position(200)
    time.sleep(5)
    controllers.motors["pitch_slider"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_position_slider"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_height"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_rotation"].go_to_speed_or_relative_position(00)
    time.sleep(5)
    controllers.motors["pitch_slider"].go_to_speed_or_relative_position(-200)
    controllers.motors["bow_position_slider"].go_to_speed_or_relative_position(-200)
    controllers.motors["bow_height"].go_to_speed_or_relative_position(-200)
    controllers.motors["bow_rotation"].go_to_speed_or_relative_position(-200)
    time.sleep(5)
    controllers.motors["pitch_slider"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_position_slider"].go_to_speed_or_relative_position(00)
    controllers.motors["bow_height"].go_to_speed_or_relative_position(0)
    controllers.motors["bow_rotation"].go_to_speed_or_relative_position(0)
    time.sleep(5)
