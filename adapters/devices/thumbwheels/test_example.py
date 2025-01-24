from thirtybirds import status_receiver
from bdc_thumbwheel import Thumbwheel

def data_receiver(wheel_value):
    print(wheel_value)

thumbwheel = Thumbwheel(
            [126,8,19,3],
            data_receiver,
            status_receiver,
            poll_interval=0.5
    )

thumbwheels = Thumbwheels(
        [
            [
                4, #bdc binary one 
                3, #bdc binary two
                2, #bdc binary four
                1 #bdc binary eight
            ], # decimal ones
            [8,7,6,5], # decimal tens
            [11,12,15,13], # decimal hundreds
            [21,22,23,9], # decimal thousands
        ],
        data_receiver,
        status_receiver,
        poll_interval=0.5
    )
