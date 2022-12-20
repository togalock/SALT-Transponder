import serial
from time import sleep
import LT_Decode_with_Factory as LT

class LT_UART:
    def __init__(self, addr, rate):
        self.addr, self.rate = addr, rate
        self.f = serial.Serial(addr, rate)
        self.buffer = []

    def poll(self):
        return self.f.readinto(self.buffer)

    def get_frame(self):
        return LT.poll_LTFrame(buffer)

    def poll_frame(self, poll_first = True):
        if poll_first: self.poll()
        frame = self.get_frame()
        if frame:
            self.buffer = self.buffer[frame[1]::]
        print(frame)

lt_uart = LT_UART("/dev/ttyS0", 115200)

while True:
    print(lt_uart.poll_frame())
