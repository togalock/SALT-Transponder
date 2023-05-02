import serial
import serial.tools.list_ports

def get_serial_interactive():
    serial_list = serial.tools.list_ports.comports()
    DEFAULT_RATE = "115200"
    DEFAULT_TIMEOUT = "0.000001"
    
    print("COMs Available: ")
    for i, port_info in enumerate(serial_list):
        print("[%i] %s" % (i, port_info.name))
    
    device = serial_list[int(input("Enter COM Index: "))].device
    baudrate = int(input("Baudrate [%s]: " % DEFAULT_RATE) or DEFAULT_RATE)
    timeout = float(input("Timeout [%s]: " % DEFAULT_TIMEOUT) or DEFAULT_TIMEOUT)
    
    return serial.Serial(port=device, baudrate=baudrate, timeout=timeout)