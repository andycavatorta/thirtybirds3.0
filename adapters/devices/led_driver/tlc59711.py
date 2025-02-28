"""
Thirtybirds Style Requirements:
    Single and multiple devices
    Synchronous requests for value
    Synchronous requests for change
    Async polling and reporting
    callback for exceptions
    callback for events
    device name can be optionally set or automatically created

    devices do not use thirtybirds
    devices do not use logging
    devices do not use the settings module directly
    devices do not call fault states

usage:

    channels = tlc59711.TLC(

    )

    channels.set_all(float)
    channels.set_value(channel_number, float)

"""

import math
import time

import adafruit_tlc59711
import board
import busio

class TLC():
    def __init__(
        self,
        exception_receiver,
        channel_quantity,
        mosi_pin=board.MOSI,
        clock_pin=board.SCK,
        device_name = None,
    ):
        self.exception_receiver = exception_receiver
        self.channel_quantity = channel_quantity
        self.mosi_pin = mosi_pin
        self.clock_pin = clock_pin
        self.device_name = (
            self.__class__.__name__ if device_name is None else device_name
        )
        self.pixel_quantity = math.ceil(channel_quantity / 3.0)
        self.luminosity_increments = 65534

        try:
            self.spi = busio.SPI(clock_pin, MOSI=mosi_pin)
            self.pixels = adafruit_tlc59711.TLC59711(
                self.spi, pixel_count=self.pixel_quantity
            )
        except Exception as e:
            self.exception_receiver(self.device_name, e)

        self.pixel_levels = []
        for i in range(self.pixel_quantity):
            self.pixel_levels.append([0, 0, 0])

    #####################
    ### P R I V A T E ###
    #####################

    def float_to_luminosity(self, luminosity_fl):
        if luminosity_fl > 1.0:
            return self.luminosity_increments
        if luminosity_fl < 0:
            return 0
        return luminosity_fl * self.luminosity_increments

    def channel_number_to_pixel_coords(self, channel_number):
        pixel_x = math.floor(channel_number / 3.0)
        pixel_y = channel_number % 3
        return (pixel_x, pixel_y)


    ###################
    ### P U B L I C ###
    ###################

    def set_value(self, channel_number, level_f):
        level_int = self.float_to_luminosity(level_f)
        pixel_coords = self.channel_number_to_pixel_coords(channel_number)
        self.pixel_levels[pixel_coords[0]][pixel_coords[1]] = level_int
        try:
            self.pixels[pixel_coords[0]] = [
                self.pixel_levels[pixel_coords[0]][0],
                self.pixel_levels[pixel_coords[0]][1],
                self.pixel_levels[pixel_coords[0]][2],
            ]
            time.sleep(0.01)
            self.pixels.show()
        except Exception as e:
            self.exception_receiver(self.device_name, e)


    def set_all_off(self):
        try:
            self.pixel_levels = [[0, 0, 0]] * self.pixel_quantity
            self.pixels.show()
        except Exception as e:
            self.exception_receiver(self.device_name, e)
