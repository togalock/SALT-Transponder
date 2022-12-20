import serial
from time import sleep
import LT_Decode_with_Factory as LT

class LT_UART:
    TIMEOUT_MS = 100

    def __init__(self, addr, rate):
        self.addr, self.rate = addr, rate
        self.f = serial.Serial(addr, rate, 
            timeout = self.TIMEOUT_MS)
        self.buffer = []

    def poll(self, size = 1):
        new_data = self.f.read(size)
        if not new_data: return None
        
        if len(new_data) == 1:
            new_byte = new_data[0]
            self.buffer.append(new_byte)
        else:
            for b in new_data:
                self.buffer.append(int(b))
        
        return len(new_data)
            
    
    def get_frame(self):
        return LT.poll_LTFrame(self.buffer)

    def poll_frame(self, poll_first = True):
        if poll_first: self.poll()
        frame = self.get_frame()
        if frame:
            self.buffer = self.buffer[frame[1]::]
        return frame

lt_uart = LT_UART("/dev/ttyS0", 115200)

while True:
    frame = lt_uart.poll_frame()
    if frame: print(frame[0].__dict__)