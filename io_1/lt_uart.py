import serial
from time import sleep
import LT_Decode_with_Factory as LT

class LT_UART:
    def __init__(self, addr, rate, timeout = 0.001):
        self.addr, self.rate = addr, rate
        self.f = serial.Serial(addr, rate, 
            timeout = timeout)
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

    def poll_frame(self, poll_size = 50, poll_first = True):
        if poll_first: self.poll(poll_size)
        frame = self.get_frame()
        if frame:
            self.buffer = self.buffer[frame[1]::]
        return frame

# lt_uart = LT_UART("/dev/ttyS0", 115200)
