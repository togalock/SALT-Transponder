import serial
import serial.tools.list_ports
import time

def get_serial_interactive():
    serial_list = serial.tools.list_ports.comports()
    DEFAULT_RATE = "115200"
    DEFAULT_TIMEOUT = "0.000001"
    
    print("COMs Available: ")
    for i, port_info in enumerate(serial_list):
        print("[%i] %s" % (i, port_info.name))
        
    use_device = input("Enter COM Index, or filename: ")
    baudrate = int(input("Baudrate [%s]: " % DEFAULT_RATE) or DEFAULT_RATE)
    timeout = float(input("Timeout [%s]: " % DEFAULT_TIMEOUT) or DEFAULT_TIMEOUT)
    
    if use_device.isdigit():
        device = serial_list[int(use_device)].device
        return serial.Serial(port=device, baudrate=baudrate, timeout=timeout)
    else:
        dummy_device = open(use_device, "rb")
        
        _read = dummy_device.read
        def read_with_timeout(size = -1):
            time.sleep(timeout)
            return _read(baudrate)
        dummy_device.read = read_with_timeout
        
        return dummy_device