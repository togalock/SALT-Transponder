import serial
from time import sleep

ser = serial. Serial ("/dev/ttyS0", 115200)

def chop_iter(_iter, chunk_sizes):
    return tuple(
        tuple(next(_iter) for _ in range(chunk_size))
        for chunk_size in chunk_sizes)
        

class LT_Loc:
    CHUNKS = (3, 2, 1, 1, 2)
    
    def __init__(self, d, a, fp, rx):
        self.d, self.a, self.fp, self.rx = d, a, fp, rx

    def __repr__(self):
        return "<LTLoc %.2f ∠%.2f (%idB)>" % (self.d, self.a, self.fp)
    
    @classmethod
    def from_iter(cls, _iter):
        d, a, fp, rx, _ = chop_iter(_iter, cls.CHUNKS)
        d, fp, rx = (int.from_bytes(_, "little") for _ in (d, fp, rx))
        a = int.from_bytes(a, "little", signed=True)
        d, a, fp, rx = d * 0.001, a * 0.01, fp * -0.5, fp * -0.5
        return cls(d, a, fp, rx)
        
class LT_Message:
    CHUNKS = (2, )
    
    def __init__(self, data, _len = None):
        self.data, self._len = data, len(data) if _len is None else _len

    def __repr__(self):
        return "<LTMsg[%i] %s>" % (self._len, self.data[0:20])
        
    @classmethod
    def from_iter(cls, _iter):
        _len = int.from_bytes(chop_iter(_iter, cls.CHUNKS)[0], "little")
        data = tuple(chop_iter(_iter, (_len, ))[0])
        return cls(data, _len)

class LT_Ident:
    CHUNKS = (1, 1)
    ROLES = {1: "ANCHOR", 2: "TAG", 6: "MONITOR"}
    
    def __init__(self, ident, role):
        self.ident, self.role = ident, role

    def __repr__(self):
        return "<LTIdent %s %s>" % (self.role_name, self.ident)

    @property
    def role_name(self):
        return self.ROLES.get(self.role, self.role)

    @classmethod
    def from_iter(cls, _iter):
        role, ident = chop_iter(_iter, cls.CHUNKS)
        role, ident = (int.from_bytes(b, "little") for b in (role, ident))
        return cls(ident, role)

class LT_Locs:
    header_chunks = (1, 1, 2, 1, 1, 4, 4, 4, 2, 1)
    
    def __init__(self, from_node, of_time, vcc, n_nodes, data):
        self.from_node, self.of_time, self.vcc, self.n_nodes, self.data = (
            from_node, of_time, vcc, n_nodes, data)

    @classmethod
    def bytes_frame_size(cls, _bytes):
        if len(_bytes) < sum(cls.header_chunks[:3]): return None
        _len = int.from_bytes(_bytes[2:4:], "little")
        return _len
    
    @staticmethod
    def bytes_is_valid(_bytes):
        sum_v, last_byte = 0, 0
        uint8_max = (1 << 8)
        for b in _bytes:
            b = int(b)
            last_byte = b
            sum_v = (sum_v + b) % uint8_max
        else:
            return last_byte == (sum_v + uint8_max - last_byte) % uint8_max
    
    @classmethod
    def from_iter(cls, _iter):
        (header, mark, _len,
        role, ident,
        local_time, system_time, _,
        vcc, n_nodes) = chop_iter(_iter, cls.header_chunks)

        assert (header[0] == 0x55) and (mark[0] == 0x07)
        
        (_len, role, ident,
        local_time, system_time,
        vcc, n_nodes) = (int.from_bytes(b, "little") for b in (
            _len, role, ident, local_time, system_time, vcc, n_nodes))

        vcc *= 0.001

        from_node = LT_Ident(ident, role)
        of_time = (local_time, system_time)

        data = []
        
        for _ in range(n_nodes):
            ident = LT_Ident.from_iter(_iter)
            loc = LT_Loc.from_iter(_iter)
            data.append((ident, loc))

        data = tuple(data)
        
        checksum = next(_iter)
        return cls(from_node, of_time, vcc, n_nodes, data)


class LT_Messages:
    header_chunks = (1, 1, 2, 1, 1, 4, 1)
    
    def __init__(self, from_node, n_nodes, data):
        self.from_node, self.n_nodes, self.data = (from_node, n_nodes, data)

    @classmethod
    def bytes_frame_size(cls, _bytes):
        if len(_bytes) < sum(cls.header_chunks[:3]): return None
        _len = int.from_bytes(_bytes[2:4:], "little")
        return _len
    
    @staticmethod
    def bytes_is_valid(_bytes):
        sum_v, last_byte = 0, 0
        uint8_max = (1 << 8)
        for b in _bytes:
            b = int(b)
            last_byte = b
            sum_v = (sum_v + b) % uint8_max
        else:
            return last_byte == (sum_v + uint8_max - last_byte) % uint8_max

    @classmethod
    def from_iter(cls, _iter):
        (header, mark, _len,
         role, ident, _, n_nodes) = chop_iter(_iter, cls.header_chunks)

        assert (header[0] == 0x55) and (mark[0] == 0x02)

        (_len, role, ident, n_nodes) = (
            int.from_bytes(b, "little")
            for b in (_len, role, ident, n_nodes))

        from_node = LT_Ident(ident, role)

        data = []
        
        for _ in range(n_nodes):
            ident = LT_Ident.from_iter(_iter)
            message = LT_Message.from_iter(_iter)
            data.append((ident, message))

        data = tuple(data)

        checksum = next(_iter)
        return cls(from_node, n_nodes, data)

def chain(*iters):
    for _iter in iters:
        for item in _iter:
            yield item

def create_LTFrame(_iter):
    header_chunks = (1, 1)
    (header, mark) = chop_iter(_iter, header_chunks)
    assert (header[0] == 0x55)

    mark_handlers = {0x02: LT_Messages.from_iter, 0x07: LT_Locs.from_iter}
    mark_handler = mark_handlers[mark[0]]
    
    return mark_handler(chain(header, mark, _iter))

def poll_LTFrame(buffer):
    header_chunks = (1, 1, 2)
    if len(buffer) < sum(header_chunks): return None

    buffer_copy = iter(buffer)
    (header, mark) = chop_iter(buffer_copy, header_chunks[:-1])
    assert (header[0] == 0x55)
    
    length_handlers = {0x02: LT_Messages.bytes_frame_size,
                       0x07: LT_Locs.bytes_frame_size}
    length_handler = length_handlers[mark[0]]
    _len = length_handler(buffer)

    if _len is None: return None
    if len(buffer) < _len: return False
    
    return (create_LTFrame(iter(buffer[:_len:])), _len)
    

def test():
    #UM Example 6.1.3.1
    SAMPLE_LOC_RAW = b'\x55\x07\x42\x00\x02\x00\xbe\x73\x02\x00\x00\x00\x00\x00\x00\x00\xf1\x06\xef\x12\x04\x01\x00\xff\x02\x00\x22\x0b\xa3\x9f\x9e\x00\x01\x01\x02\x03\x00\xad\x00\xa4\x9f\x00\x00\x01\x02\xec\x03\x00\xcb\x03\xa5\xa0\x00\x00\x01\x03\x88\x05\x00\x99\xec\xa3\xa0\x00\x00\x33'
    print(LT_Locs.bytes_is_valid(SAMPLE_LOC_RAW))
    print(LT_Locs.from_iter(iter(SAMPLE_LOC_RAW)).__dict__)

    #UM Example 6.1.3.4
    SAMPLE_MSG_RAW = b'\x55\x02\x19\x00\x01\x00\xef\x72\x02\x32\x01\x02\x00\x09\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\x0f'
    print(LT_Messages.bytes_is_valid(iter(SAMPLE_MSG_RAW)))
    print(LT_Messages.from_iter(iter(SAMPLE_MSG_RAW)).__dict__)

    # Determining
    print(create_LTFrame(iter(SAMPLE_LOC_RAW)))
    print(create_LTFrame(iter(SAMPLE_MSG_RAW)))

    # Overpolling
    buffer = tuple(SAMPLE_LOC_RAW) + tuple(SAMPLE_MSG_RAW)
    for _ in range(3):
        frame = poll_LTFrame(buffer)
        if frame:
            buffer = buffer[frame[1]::]
        print(frame)

#if __name__ == "__main__":
#    test()

while True:
    received_data = ser.read()
    if received_data == b'\x55':
        received_data += ser.read()
        frame_length_raw = ser.read()
        frame_length_raw += ser.read()
        frame_length = int.from_bytes(frame_length_raw, "little")
        received_data += frame_length_raw
        received_data += ser.read(frame_length - 4)
        print(received_data)
    translated_data_1 = iter(received_data)
    translated_data_2 = iter(received_data)
    print(LT_Locs.bytes_is_valid(translated_data_1))
    print(LT_Locs.from_iter(translated_data_2).__dict__)
    
