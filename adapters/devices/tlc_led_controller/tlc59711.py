"""
format for channel_names
["a","b","c","d","e","f","g","h"]

level is between 0.0 - 1.0

single_channels.set_channel_level(channel_number,level_f)

single_channels["a"].set_level(0.5)

"""

import math
import time

from keyword import iskeyword

import adafruit_tlc59711
import board
import busio

class NameMethods:
    """
    to do: finish docstring
    """

    def __init__(self, channel_number, set_channel_level):
        """
        to do: finish docstring
        """
        self.channel_number = channel_number
        self.set_channel_level = set_channel_level

    def set_level(self,level_f):
        """
        to do: finish docstring
        """
        self.set_channel_level(self.channel_number, level_f)

    def set_off(self):
        """
        to do: finish docstring
        """
        self.set_channel_level(self.channel_number, 0)


def float_to_luminosity(luminosity_fl):
    """
    to do: finish docstring
    """
    if luminosity_fl > 1.0:
        return 0
    if luminosity_fl < 0:
        return 0
    return luminosity_fl * 50000  # 65535

def channel_number_to_pixel_coords(channel_number):
    """
    to do: finish docstring
    """
    pixel_x = math.floor(channel_number / 3.0)
    pixel_y = channel_number % 3
    return (pixel_x, pixel_y)



class SingleChannels:
    """
    to do: finish docstring
    """

    def __init__(
        self,
        status_receiver,
        channel_quantity,
        channel_names = None,
        mosi_pin=board.MOSI,
        clock_pin=board.SCK,
    ):
        """
        to do: finish docstring
        """
        self.status_receiver = status_receiver
        self.pixel_quantity = math.ceil(channel_quantity / 3.0)
        self.channel_names = [] if channel_names is None else channel_names
        self.spi = busio.SPI(clock_pin, MOSI=mosi_pin)
        self.pixels = adafruit_tlc59711.TLC59711(
            self.spi, pixel_count=self.pixel_quantity
        )
        self.named_channels = {}
        self.pixel_levels = []
        for i in range(self.pixel_quantity):
            self.pixel_levels.append([0, 0, 0])
        if len(self.channel_names) == channel_quantity:
            print("aa")
            if len([name for name in self.channel_names if iskeyword(name)])== 0:
                print("bb")
                if ([name for name in self.channel_names if name.isidentifier()]) == 0:
                    print("cc")
                    for i, name in enumerate(self.channel_names):
                        print("dd",name)
                        if name != "":
                            print("ee",name)
                            self.named_channels[name] = NameMethods(self.set_channel_level, i)
                            #setattr(self, name, NameMethods(self.set_channel_level, i))
        self.status_receiver.collect(
            self.status_receiver.capture_local_details.get_location(self),
            "started",
            self.status_receiver.Types.INITIALIZATIONS,
        )

    def set_channel_level(
        self, channel_number, level_f
    ):  # level_f should be between 0.0 and 1.0
        """
        to do: finish docstring
        """
        level_int = float_to_luminosity(level_f)
        pixel_coords = channel_number_to_pixel_coords(channel_number)
        self.pixel_levels[pixel_coords[0]][pixel_coords[1]] = level_int
        self.pixels[pixel_coords[0]] = [
            self.pixel_levels[pixel_coords[0]][0],
            self.pixel_levels[pixel_coords[0]][1],
            self.pixel_levels[pixel_coords[0]][2],
        ]
        time.sleep(0.01)
        self.pixels.show()

    def set_all_off(self):
        """
        to do: finish docstring
        """
        self.pixel_levels = [[0, 0, 0]] * self.pixel_quantity
        self.pixels.show()


###############
### T E S T ###
###############

class CaptureLocalDetails:
    def __init__(self):
        pass

    def get_location(self, *args):
        pass

class Status_Receiver_Stub:
    capture_local_details = CaptureLocalDetails()

    class Types:
        INITIALIZATIONS = "INITIALIZATIONS"

    def __init__(self):
        pass

    def collect(self, *args):
        pass

def data_callback(current_value):
    print(current_value)

test_channel_names = [
    "", # 0
    "", # 1
    "", # 2
    "", # 3
    "", # 4
    "", # 5
    "", # 6
    "", # 7
    "", # 8
    "", # 9
    "", # 0
    "", # 11
    "BALL_UNDERCOUNT", # 12
    "TRAPDOOR_SENSOR", # 13
    "TRAPDOOR_TEMP", # 14
    "", # 15
    "", # 16
    "TRAPDOOR_MOTION", # 17
    "", # 18
    "", # 19
    "", # 20
    "", # 21
    "", # 22
    "", # 23
    "TURNSTILE_TEMP", # 24
    "TURNSTILE_BOTTOM", # 25
    "TURNSTILE_ENCODER", # 26
    "LIFTER_BOTTOM", # 27
    "LIFTER_TEMP", # 28
    "", # 29
    "", # 30
    "LIFTER_TOP", # 31
    "", # 32
    "", # 33
    "", # 34
    "", # 35
    "HIGH_POWER", # 36
    "RAY_STARTED", # 37
    "CHARLES_STARTED", # 38
    "TURNSTILE_TOP", # 39
    "TURNSTILE_MOTION", # 40
    "BALL_EXPECTED", # 41
    "", # 42
    "", # 43
    "", # 44
    "", # 45
    "", # 46
    "", # 47
]



def make_tlc():
    return SingleChannels(
            Status_Receiver_Stub(),
            48,
            test_channel_names,
    )



"""
def data_callback(name, position):
    print(name, position)

class Status_Receiver_Stub:
    class Types:
        INITIALIZATIONS = "INITIALIZATIONS"

    def __init__(self):
        pass

    def collect(self, *args):
        pass

single_channels = None
def test(channel_quantity,channel_names):
    global single_channels
    single_channels =  SingleChannels(
        channel_quantity,
        Status_Receiver_Stub(),
        channel_names
    )
"""
