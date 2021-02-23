"""
add status message feedback
include buttons if useful
"""
import mido
import threading
import time

class Main(threading.Thread):
    def __init__(self, 
            hostname,
            midi_receiver):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.midi_receiver = midi_receiver
        self.input_name = ""
        self.start()
        
    def run(self):
        while True:
            try:
                with mido.open_input(self.input_name) as inport:
                    print("midi connected")
                    for midi_o in inport:
                        #print(midi_o)
                        if midi_o.type == "note_on":
                            self.midi_receiver("oxygen88", ["note_on", midi_o.note], self.hostname, self.hostname)
                            continue
                        if midi_o.type == "note_off":
                            self.midi_receiver("oxygen88",["note_off", midi_o.note], self.hostname, self.hostname)
                            continue
                        if midi_o.type == "control_change":
                            if midi_o.control == 74: 
                                self.midi_receiver("oxygen88",["slider1", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 71: 
                                self.midi_receiver("oxygen88",["slider2", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 91: 
                                self.midi_receiver("oxygen88",["slider3", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 93: 
                                self.midi_receiver("oxygen88",["slider4", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 73: 
                                self.midi_receiver("oxygen88",["slider5", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 72: 
                                self.midi_receiver("oxygen88",["slider6", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 5: 
                                self.midi_receiver("oxygen88",["slider7", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 84:
                                self.midi_receiver("oxygen88",["slider8", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 7:
                                self.midi_receiver("oxygen88",["slider9", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 75:
                                self.midi_receiver("oxygen88",["knob1", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 76:
                                self.midi_receiver("oxygen88",["knob2", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 92:
                                self.midi_receiver("oxygen88",["knob3", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 95:
                                self.midi_receiver("oxygen88",["knob4", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 10:
                                self.midi_receiver("oxygen88",["knob5", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 77:
                                self.midi_receiver("oxygen88",["knob6", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 78:
                                self.midi_receiver("oxygen88",["knob7", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 78:
                                self.midi_receiver("oxygen88",["knob8", midi_o.value], self.hostname, self.hostname)
                                continue
                            if midi_o.control == 1:
                                self.midi_receiver("oxygen88",["modwheel", midi_o.value], self.hostname, self.hostname)
                                continue
                        if midi_o.type == "pitchwheel":
                                self.midi_receiver("oxygen88",["pitchwheel", midi_o.pitch], self.hostname, self.hostname)
                                continue
            except OSError as e:
                input_names = mido.get_input_names()
                for input_name in input_names:
                    if input_name.startswith("Oxygen"):
                        self.input_name = input_name
                        continue
                #print(input_names)
                time.sleep(5)
