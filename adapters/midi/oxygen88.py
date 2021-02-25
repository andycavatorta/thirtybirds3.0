import mido
import threading

from thirtybirds3 import thirtybirds
#from thirtybirds3.dev.hid.oxygen88 import oxygen88

class MIDI(threading.Thread):
    def __init__(self, hostname):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.start()
        
    def run(self):
        try:
            with mido.open_input("Oxygen 88:Oxygen 88 MIDI 1 20:0") as inport:
                print("midi connected")
                for midi_o in inport:
                    print(midi_o)
                    if midi_o.type == "note_on":
                        main.add_to_queue("note_on", midi_o.note, self.hostname, self.hostname)
                        continue
                    if midi_o.type == "note_off":
                        main.add_to_queue("note_off", midi_o.note, self.hostname, self.hostname)
                        continue
                    if midi_o.type == "control_change":
                        if midi_o.control == 74: 
                            main.add_to_queue("slider1", midi_o.value, self.hostname, self.hostname)
                            continue
                        if midi_o.control == 71: 
                            main.add_to_queue("slider2", midi_o.value, self.hostname, self.hostname)
                            continue
                        if midi_o.control == 91: 
                            main.add_to_queue("slider3", midi_o.value, self.hostname, self.hostname)
                            continue
                        if midi_o.control == 93: 
                            main.add_to_queue("slider4", midi_o.value, self.hostname, self.hostname)
                            continue
                        if midi_o.control == 73: 
                            main.add_to_queue("slider5", midi_o.value, self.hostname, self.hostname)
                            continue
                        if midi_o.control == 72: 
                            main.add_to_queue("slider6", midi_o.value, self.hostname, self.hostname)
                            continue
                        if midi_o.control == 5: 
                            main.add_to_queue("slider7", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 84:
                            main.add_to_queue("slider8", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 7:
                            main.add_to_queue("slider9", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 75:
                            main.add_to_queue("knob1", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 76:
                            main.add_to_queue("knob2", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 92:
                            main.add_to_queue("knob3", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 95:
                            main.add_to_queue("knob4", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 10:
                            main.add_to_queue("knob5", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 77:
                            main.add_to_queue("knob6", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 78:
                            main.add_to_queue("knob7", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 78:
                            main.add_to_queue("knob8", midi_o.value, self.hostname, self.hostname)
                            pass
                        if midi_o.control == 1:
                            main.add_to_queue("modwheel", midi_o.value, self.hostname, self.hostname)
                            pass
                    if midi_o.type == "pitchwheel":
                        if midi_o.control == :
                            main.add_to_queue("pitchwheel", midi_o.pitch, self.hostname, self.hostname)
                            pass
        except OSError as e:
            time.sleep(5)
