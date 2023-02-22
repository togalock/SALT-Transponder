from functools import partial

uint = partial(int.from_bytes, byteorder="little", signed=False)
rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r

# Uses chunks of (start, stop); Pre-computes for better performance
map_bytes = lambda b, chunk_lens: map(lambda chunk: uint(b[chunk[0]:chunk[1]]), chunk_lens)

class LT_Loc:
    def __init__(self, role, rid, d, a, fp, rx):
        self.role, self.rid, self.d, self.a, self.fp, self.rx = role, rid, d, a, fp, rx

    def __repr__(self):
        return "<LTLoc %.2f ∠%.2f (fp=%idB)>" % (self.d, deg(self.a), self.fp)
    
    @classmethod
    def from_bytes(cls, b):
        if len(b) < 11: return None
        chunk_lens = ((0, 1), (1, 2), (2, 5), (5, 7), (7, 8), (8, 9), (9, 11))
        role, rid, d, a, fp, rx, _ = map_bytes(b, chunk_lens)
        # From uint16 to int16,
        # 2's complement has first bit as negative
        # (0x1011 = -8 + 0 + 2 + 1 = -5)
        a = rad(0.01 * (((a >> 15) * (-1 << 16)) + a))

        return cls(role, rid, d, a, fp, rx)


class LT_Message:
    def __init__(self, role, rid, len_, data):
        self.role, self.rid, self.len_, self.data = role, rid, len_, data

    def __repr__(self):
        return "<LTMsg[%i] %s>" % (self.len_, self.data[0:20])

    @classmethod
    def from_bytes(cls, b):
        if len(b) < 4: return None
        chunk_lens = ((0, 1), (1, 2), (2, 4))
        role, rid, len_ = map_bytes(b, chunk_lens)
        if len(b) < len_: return None
        data = b[5:5 + len_]

        return cls(role, rid, len_, data)


class LT_Locs:
    def __init__(self, len_, role, rid, local_time, sys_time, vcc, n_nodes, lt_locs):
        self.len_, self.role, self.rid, self.local_time, self.sys_time, self.vcc, self.n_nodes, self.lt_locs = \
                  len_, role, rid, local_time, sys_time, vcc, n_nodes, lt_locs

    @classmethod
    def from_bytes(cls, b):
        if len(b) < 21: return None
        if (b[0] != 0x55) or (b[1] != 0x07): return False
        
        chunk_lens = ((0, 1), (1, 2), (2, 4), (4, 5), (5, 6), (6, 10), (10, 14), (14, 18), (18, 20), (20, 21))
        header, mark, len_, role, rid, local_time, sys_time, _, vcc, n_nodes = map_bytes(b, chunk_lens)

        if len(b) < len_: return None
        
        lt_locs = []
        checksum, CHECKSUM_ENABLED = sum(b[0:21]) & ((1 << 8) - 1), True
        
        for i in range(21, 21 + n_nodes * 11, 11):
            block = b[i:i + 11]
            lt_loc = LT_Loc.from_bytes(block)
            if not lt_loc:
                return lt_loc
            else:
                lt_locs.append(lt_loc)

            if CHECKSUM_ENABLED:
                checksum = (checksum + sum(block)) & ((1 << 8) - 1)
        
        if CHECKSUM_ENABLED:
            if b[len_ - 1] != checksum: return False

        return cls(len_, role, rid, local_time, sys_time, vcc, n_nodes, lt_locs)


class LT_Messages:
    def __init__(self, len_, role, rid, n_nodes, lt_messages):
        self.len_, self.role, self.rid, self.n_nodes, self.lt_messages = \
                   len_, role, rid, n_nodes, lt_messages

    @classmethod
    def from_bytes(cls, b):
        if len(b) < 21: return None
        if (b[0] != 0x55) or (b[1] != 0x02): return False

        chunk_lens = ((0, 1), (1, 2), (2, 4), (4, 5), (5, 6), (6, 10), (10, 11))
        header, mark, len_, role, rid, _, n_nodes = map_bytes(b, chunk_lens)
        
        if len(b) < len_: return None

        lt_messages = []
        checksum, CHECKSUM_ENABLED = sum(b[0:11]) & ((1 << 8) - 1), True
        cursor = 11

        for _ in range(n_nodes):
            block_len = uint(b[cursor + 2:cursor + 4])
            block = b[cursor:cursor + block_len + 4]
            lt_message = LT_Message.from_bytes(block)
            if not lt_message:
                return lt_message
            else:
                lt_messages.append(lt_message)
                cursor += lt_message.len_

            if CHECKSUM_ENABLED:
                checksum = (checksum + sum(block)) & ((1 << 8) - 1)

        if CHECKSUM_ENABLED:
            if b[len_ - 1] != checksum: return False

        return cls(len_, role, rid, n_nodes, lt_messages)


class LTQueue:
    def __init__(self, init_bytes = b''):
        self.buffer = bytearray(init_bytes)

    def pop(self):
        # Returns: False: Frame malformed; None: Frame incomplete;
        # (Type, Object): 1 decoded frame
        b = self.buffer

        # Blocks without the header are malformed and should be dropped
        # Default to look 20 bytes ahead only to allow mainloop to continue
        block_offset, frame_type = b.find(0x55, 0, 21), None
        if block_offset > -1:
            frame_type = b[block_offset + 1]
            del self.buffer[:block_offset]
        else:
            frame_type = False
            del self.buffer[:20]
        
        lt_frame = None
        if frame_type:
            if frame_type == 0x02:
                lt_frame = LT_Messages.from_bytes(b)
            elif frame_type == 0x07:
                lt_frame = LT_Locs.from_bytes(b)
            else:
                pass

        if lt_frame:
            del self.buffer[:lt_frame.len_]
        # If frame is malformed, then 0x55 is part of missing data
        # dropping with same criteria as above
        elif lt_frame is False:
            del self.buffer[:20]
        else:
            pass
            
        return (frame_type, lt_frame)

    def write(self, b):
        self.buffer.extend(b)

def test():
    lt_queue = LTQueue()
    
    #UM Example 6.1.3.1
    SAMPLE_LOC_RAW = b'\x55\x07\x42\x00\x02\x00\xbe\x73\x02\x00\x00\x00\x00\x00\x00\x00\xf1\x06\xef\x12\x04\x01\x00\xff\x02\x00\x22\x0b\xa3\x9f\x9e\x00\x01\x01\x02\x03\x00\xad\x00\xa4\x9f\x00\x00\x01\x02\xec\x03\x00\xcb\x03\xa5\xa0\x00\x00\x01\x03\x88\x05\x00\x99\xec\xa3\xa0\x00\x00\x33'

    #UM Example 6.1.3.4
    SAMPLE_MSG_RAW = b'\x55\x02\x19\x00\x01\x00\xef\x72\x02\x32\x01\x02\x00\x09\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\x0f'

    lt_queue.write(SAMPLE_LOC_RAW)
    lt_queue.write(SAMPLE_MSG_RAW)

    for _ in range(3):
        frame = lt_queue.pop()
        print(frame, frame[1].__dict__ if frame[1] else frame[1])

if __name__ == "__main__":
    test()
