import serial
from time import sleep

#ser = serial.Serial ("/dev/ttyS0", 115200)

class uart(object):

    def __init__(self):
        self.ser = serial.Serial ("/dev/ttyS0", 115200)

    def read(self):
        received_data = self.ser.read()
        if received_data == b'\x55':
            received_data += self.ser.read()
            frame_length_raw = self.ser.read()
            frame_length_raw += self.ser.read()
            frame_length = int.from_bytes(frame_length_raw, "little")
            received_data += frame_length_raw
            received_data += self.ser.read(frame_length - 4)
            print(received_data)
        return(received_data)
