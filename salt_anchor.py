from uart import *
from LT_Decode_with_Factory import *

serial = uart()

while True:
    received_data = serial.read()
    data = iter(received_data)
    print(LT_Locs.from_iter(data).__dict__)
