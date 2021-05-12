#!/usr/bin/env python

'''
run like this:
python setOverheadValues.py 123 129
to test values from 123 to 129, etc.
'''

import time
import math
import sys

import HC595_shift_reg as shifter

reg = shifter.HC595()

shift_register_state = [0, 0, 0, 0, 0]


def turn_on_light(trk_value):

    shift_register_state[0] = shift_register_state[0] + (1 << trk_value)

    reg.write(shift_register_state)

'''
'''

word = ""
global num

# def set_number():
#     turn_off_lights()
#     # 7
#     num = str(num)
#     # Make sure 7 goes to 007 and 37 goes to 037
#     num = ("0" + num) if len(num) == 1 else num
#     num = ("0" + num) if len(num) == 2 else num

#     # For each number of 007 look up the correct shift reg and bit to flip
#     for index, number in enumerate(num):
#         shift_register_index = shift_reg_mapping["display_number"][index][int(number)]["shift_register_index"]
#         bit = shift_reg_mapping["display_number"][index][int(number)]["bit"]
#         shift_register_state[shift_register_index] = shift_register_state[shift_register_index] + (1 << bit)
#     set_word()
#     update_display()


# def set_word():
#     turn_off_lights()
#     shift_register_index = shift_reg_mapping["display_sentence"][game_state]["shift_register_index"]
#     bit = shift_reg_mapping["display_number"][game_state]["bit"]

#     # Turn on state for word
#     shift_register_state[shift_register_index] = shift_register_state[shift_register_index] + (1 << bit)

#     set_number()
#     update_display()

# def turn_off_lights():
#     for shift_register_value in shift_register_state:
#         shift_register_value = 0x00

#     reg.write(shift_register_state)

# def update_display():
#     # turn_off_lights()
#     # set_number()
#     # set_word()
#     reg.write(shift_register_state)
class Acrylic_Display():
    def __init__(self):
        self.current_words = 0
        self.current_number = 0
        self.game_mode = "countdown"
        self.shift_register_state = [0, 0, 0, 0, 0]
        self.reg = shifter.HC595()
        self.Display_LED_Mapping = {
            "display_number":  {
                0: {
                    0: {"bit": 0, "shift_register_index": 0},
                    1: {"bit": 1, "shift_register_index": 0},
                    2: {"bit": 2, "shift_register_index": 0},
                    3: {"bit": 3, "shift_register_index": 0},
                    4: {"bit": 4, "shift_register_index": 0},
                    5: {"bit": 5, "shift_register_index": 0},
                    6: {"bit": 6, "shift_register_index": 0},
                    7: {"bit": 7, "shift_register_index": 0},
                    8: {"bit": 0, "shift_register_index": 1},
                    9: {"bit": 1, "shift_register_index": 1}
                },
                1: {
                    0: {"bit": 2, "shift_register_index": 1},
                    1: {"bit": 3, "shift_register_index": 1},
                    2: {"bit": 4, "shift_register_index": 1},
                    3: {"bit": 5, "shift_register_index": 1},
                    4: {"bit": 6, "shift_register_index": 1},
                    5: {"bit": 7, "shift_register_index": 1},
                    6: {"bit": 0, "shift_register_index": 2},
                    7: {"bit": 1, "shift_register_index": 2},
                    8: {"bit": 2, "shift_register_index": 2},
                    9: {"bit": 3, "shift_register_index": 2}
                },
                2: {
                    0: {"bit": 0, "shift_register_index": 3},
                    1: {"bit": 1, "shift_register_index": 3},
                    2: {"bit": 2, "shift_register_index": 3},
                    3: {"bit": 3, "shift_register_index": 3},
                    4: {"bit": 4, "shift_register_index": 3},
                    5: {"bit": 5, "shift_register_index": 3},
                    6: {"bit": 6, "shift_register_index": 3},
                    7: {"bit": 7, "shift_register_index": 3},
                    8: {"bit": 0, "shift_register_index": 4},
                    9: {"bit": 1, "shift_register_index": 4}
                }
            },
            "display_sentence": {
                "countdown":         {"bit": 2, "shift_register_index": 4},
                "barter_mode_intro": {"bit": 3, "shift_register_index": 4},
                "barter_mode":       {"bit": 4, "shift_register_index": 4},
                "money_mode":        {"bit": 5, "shift_register_index": 4},
                "money_mode_intro":  {"bit": 6, "shift_register_index": 4}
            }
        }

    def format_number(self, num):
        num = str(num)
        # Make sure 7 goes to 007 and 37 goes to 037
        num = ("0" + num) if len(num) == 1 else num
        num = ("0" + num) if len(num) == 2 else num
        return num

    def set_number(self, num):
        self.current_number = self.format_number(num)
        print("setting num to ", self.current_number)
        self._update_display_()

    def generate_number_bytes(self):
        # For each number of 007 look up the correct shift reg and bit to flip
        for index, number in enumerate(self.current_number):
            print( f'index:{index}, number:{number}' )
            shift_register_index = self.Display_LED_Mapping[
                "display_number"][index][int(number)]["shift_register_index"]
            print("Writing value at  shift register index ", shift_register_index)

            bit = self.Display_LED_Mapping["display_number"][index][int(
                number)]["bit"]
            print(f"Current Shift Reg: '{self.shift_register_state}. Writing bit { bit } at index {shift_register_index}")
            self.shift_register_state[shift_register_index] = self.shift_register_state[shift_register_index] + (
                1 << bit)
            print("Current state of shift reg: ", self.shift_register_state)

    def set_words(self):
        self.current_words = self.game_mode
        self._update_display_()

    def generate_word_bytes(self):
        shift_register_index = self.Display_LED_Mapping[
            "display_sentence"][self.game_mode]["shift_register_index"]
        bit = self.Display_LED_Mapping["display_sentence"][self.game_mode]["bit"]

        # Turn on state for word
        self.shift_register_state[shift_register_index] = self.shift_register_state[shift_register_index] + (
            1 << bit)

    def turn_off_lights(self):
        print("Turning off")
        for index, val in enumerate(self.shift_register_state):
            self.shift_register_state[index] = 0x00
        print("Clean state now", self.shift_register_state)
        self.reg.write(self.shift_register_state)

    def _update_display_(self):
        self.turn_off_lights()
        self.generate_number_bytes()
        # self.generate_word_bytes()
        self.reg.write(self.shift_register_state)
        print("updating display to Current Word {} Number {}".format(
            self.current_words, self.current_number))


# this is put inside a try block so it can clean up
# the output enable.  very important to protect relays from
# being left on!!!!
try:
    val = [0, 0, 0, 0, 0]
    display = Acrylic_Display()
    ontime = 1
    counterVal = int( sys.argv[ 1 ] )
    while True:

        print()

        # if topic == b'set_number':
        #     num = 123
        #     update_display()
        # num = 0
        # display.set_number("0")
        # # # val[ 0 ] = val[ 0 ] + ( 1 << 0 )
        # # # display.reg.write(val)
        # time.sleep(ontime)
        # display.turn_off_lights()
        # time.sleep(ontime)

        # display.set_number("123")
        #display.set_number("200")
        display.set_number( str( counterVal ) )
        print()
        counterVal = counterVal + 1
        # print( f"{ sys.argv[1] } { sys.argv[2]} " )
        if counterVal > int( sys.argv[2] ):
            if len( argv[2] ) < 2:
                sys.exit()
            counterVal = int( sys.argv[1] )
        
        # # val[ 0 ] = val[ 0 ] + ( 1 << 0 )
        # # display.reg.write(val)
        time.sleep(ontime)
        #display.turn_off_lights()
        #time.sleep(ontime)

        # display.set_number("200")
        # # # val[ 0 ] = val[ 0 ] + ( 1 << 0 )
        # # # display.reg.write(val)
        # time.sleep(ontime)
        # display.turn_off_lights()
        # time.sleep(ontime)


except KeyboardInterrupt:
    print("You've exited the program.")

finally:
    print("cleaning up GPIO now.")
    reg.disable_Output_Enable()
