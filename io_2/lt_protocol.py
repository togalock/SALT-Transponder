import typing as ty
import functools as ff
import time

# Uses ns as multiple is faster than divide
now = lambda: int(0.001 * time.time_ns())

uint = ff.partial(int.from_bytes, byteorder="little", signed=False)
# From uint to int,
# 2's complement has first bit as negative
# (0x1011 = -8 + 0 + 2 + 1 = -5)
sint = lambda unsigned, bits = 8: (unsigned >> bits - 1) * (-1 << bits) + unsigned

rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r

MCS = 100000

def range_chunks(*chunks):
    res, start = [], 0
    for chunk in chunks:
        res.append((start, start + chunk))
        start += chunk
    
    return tuple(res)

# Uses chunks of (start, stop); Pre-computes for better performance
map_bytes = lambda b, chunk_lens, start=0: map(
    lambda chunk: uint(b[start + chunk[0] : start + chunk[1]]), chunk_lens
)

# Units: t (us), a (rad), d (mm)

class LT_Loc:
    def __init__(self, role: int, rid: int, d, a, fp, rx):
        # fp: First Path dB; rx: Average dB
        self.role, self.rid, self.d, self.a, self.fp, self.rx = role, rid, d, a, fp, rx
        self.checksum = None

    def __repr__(self):
        return "<LTLoc %.2f ∠%.2f (fp=%idB)>" % (self.d, deg(self.a), self.fp)

    @classmethod
    def from_bytes(cls, b: bytes, start=0):
        if len(b) - start < 11:
            return None
        chunk_lens = range_chunks(1, 1, 3, 2, 1, 1, 2)
        role, rid, d, a, fp, rx, _ = map_bytes(b, chunk_lens, start)
        a = rad(0.01 * sint(a, 16))

        res = cls(role, rid, d, a, fp, rx)
        res.checksum = sum(b[start : start + 11]) & ((1 << 8) - 1)

        return res


class LT_Message:
    def __init__(self, role, rid, len_, data):
        self.role, self.rid, self.len_, self.data = role, rid, len_, data
        self.checksum = None

    def __repr__(self):
        return "<LTMsg[%i] %s>" % (self.len_, self.data)

    @classmethod
    def from_bytes(cls, b: bytes, start=0):
        readable_length = len(b) - start
        if readable_length < 4:
            return None
        chunk_lens = ((0, 1), (1, 2), (2, 4))
        role, rid, len_ = map_bytes(b, chunk_lens, start)
        if readable_length < len_:
            return None
        data = b[start + 5 : start + 5 + len_]

        res = cls(role, rid, len_, data)
        res.checksum = sum(b[start : start + len_ + 4]) & ((1 << 8) - 1)

        return res


class LT_Locs:
    def __init__(self, len_, role, rid, local_time, sys_time, vcc, n_nodes, lt_locs):
        (
            self.len_,
            self.role,
            self.rid,
            self.local_time,
            self.sys_time,
            self.vcc,
            self.n_nodes,
            self.lt_locs,
        ) = (len_, role, rid, local_time, sys_time, vcc, n_nodes, lt_locs)

    @classmethod
    def from_bytes(cls, b: bytes, start=0):
        readable_length = len(b) - start
        if readable_length < 21:
            return None
        if (b[start] != 0x55) or (b[start + 1] != 0x07):
            return False

        chunk_lens = range_chunks(1, 1, 2, 1, 1, 4, 4, 4, 2, 1)
        (_header, _mark, len_, role, rid, local_time, sys_time, _, vcc, n_nodes, ) = \
                  map_bytes(b, chunk_lens, start)

        if readable_length < len_:
            return None

        lt_locs = []
        CHECKSUM_ENABLED = True
        checksum = sum(b[start : start + 21]) & ((1 << 8) - 1)

        for i in range(start + 21, start + 21 + n_nodes * 11, 11):
            lt_loc = LT_Loc.from_bytes(b, start=i)
            if not lt_loc:
                return lt_loc
            else:
                lt_locs.append(lt_loc)

            if CHECKSUM_ENABLED:
                checksum = (checksum + lt_loc.checksum) & ((1 << 8) - 1)

        if CHECKSUM_ENABLED:
            if b[start + len_ - 1] != checksum:
                return False

        return cls(len_, role, rid, local_time, sys_time, vcc, n_nodes, lt_locs)


class LT_Messages:
    def __init__(self, len_, role, rid, n_nodes, lt_messages):
        self.len_, self.role, self.rid, self.n_nodes, self.lt_messages = (
            len_, role, rid, n_nodes, lt_messages,)

    @classmethod
    def from_bytes(cls, b: bytes, start=0):
        readable_length = len(b) - start
        if readable_length < 21:
            return None
        if (b[start] != 0x55) or (b[start + 1] != 0x02):
            return False

        chunk_lens = range_chunks(1, 1, 2, 1, 1, 4, 1)
        _header, _mark, len_, role, rid, _, n_nodes = map_bytes(b, chunk_lens, start)

        if readable_length < len_:
            return None

        lt_messages = []
        CHECKSUM_ENABLED = True
        checksum = sum(b[start : start + 11]) & ((1 << 8) - 1)
        cursor = start + 11

        for _ in range(n_nodes):
            lt_message = LT_Message.from_bytes(b, cursor)
            if not lt_message:
                return lt_message
            else:
                lt_messages.append(lt_message)
                if CHECKSUM_ENABLED:
                    checksum = (checksum + lt_message.checksum) & ((1 << 8) - 1)
                cursor += lt_message.len_

        if CHECKSUM_ENABLED:
            if b[start + len_ - 1] != checksum:
                return False

        return cls(len_, role, rid, n_nodes, lt_messages)

class FrameRanges(ty.TypedDict):
    is_complete: bool
    mark: int
    start: int
    actual_len: int
    stated_len: int


class LTQueue:
    def __init__(self, init_bytes=b""):
        self.buffer = bytearray(init_bytes)
        self.write_times: list[int, int] = []  # [[Time, Frames Read]]

    def get_frame_ranges(self, n=10, start=0) -> tuple[int, dict[FrameRanges]]:
        # Returns [Scan End Index, [
        # {is_complete, mark, start (cursor), actual_len, stated_len}, ...]]
        MAX_LOOKAHEAD = 21
        MAX_FRAMES = n

        b = self.buffer
        cursor = start
        
        bytes_scanned = min(cursor, len(b))
        frame_ranges = []
        
        for _ in range(MAX_FRAMES):
            bytes_scanned = cursor
            cursor = b.find(0x55, cursor, cursor + MAX_LOOKAHEAD)
            if cursor < 0 or len(b) - cursor < 4:
                break

            chunk_lens = range_chunks(1, 1, 2)
            _header, mark, len_ = map_bytes(b, chunk_lens, cursor)
            actual_len = min(len(b) - cursor, len_)
            is_complete = actual_len >= len_
            frame_ranges.append({
                "is_complete": is_complete,
                "mark": mark,
                "start": cursor,
                "actual_len": actual_len,
                "stated_len": len_
                })

            cursor += len_

        return (bytes_scanned, frame_ranges)

    def write(self, b, time=None) -> ty.Union[None, tuple[int, int]]:
        # Returns None, or [time, new_frames_count]
        if time is None: time = now()
        if len(b) <= 0: return None
        
        old_b_ends = self.get_frame_ranges()[0]

        self.buffer.extend(b)

        frames_added = len(self.get_frame_ranges(start=old_b_ends)[1])
        if frames_added <= 0: return None
        
        res = [time, frames_added]
        self.write_times.append(res)

        return res
    
    def pops(self, n=10):
        _, frame_ranges = self.get_frame_ranges(n = n)
        res = []
        pop_bytes = max(frame_range["start"] + frame_range["actual_len"] \
                        if frame_range["is_complete"] else 0 \
                        for frame_range in frame_ranges) if frame_ranges else 0
        
        for frame_range in frame_ranges:
            self.write_times = [write_time
                                for write_time in self.write_times
                                if write_time[1] > 0]
            if len(self.write_times) <= 0 or not frame_range["is_complete"]:
                break
            
            timestamp = self.write_times[0][0]
            
            if not frame_range["is_complete"]:
                res.append([timestamp, None])
            elif frame_range["mark"] == 0x02:
                res.append([timestamp, LT_Messages.from_bytes(self.buffer, start=frame_range["start"])])
            elif frame_range["mark"] == 0x07:
                res.append([timestamp, LT_Locs.from_bytes(self.buffer, start=frame_range["start"])])
            else:
                res.append([timestamp, False])

            self.write_times[0][1] -= 1
        
        del self.buffer[:pop_bytes]
                                              
        return res
        
    
    def pops_after(self, time=0, n=10):
        drop_frames = sum(write_time[1] if write_time[0] < time else 0 for write_time in self.write_times)
        drop_bytes, _ = self.get_frame_ranges(n = drop_frames)
        self.write_times = [write_time for write_time in self.write_times if write_time[0] >= time]
        del self.buffer[:drop_bytes]
        
        return self.pops(n = n)
    
    

def test():
    lt_queue = LTQueue()

    # UM Example 6.1.3.1
    SAMPLE_LOC_RAW = b"\x55\x07\x42\x00\x02\x00\xbe\x73\x02\x00\x00\x00\x00\x00\x00\x00\xf1\x06\xef\x12\x04\x01\x00\xff\x02\x00\x22\x0b\xa3\x9f\x9e\x00\x01\x01\x02\x03\x00\xad\x00\xa4\x9f\x00\x00\x01\x02\xec\x03\x00\xcb\x03\xa5\xa0\x00\x00\x01\x03\x88\x05\x00\x99\xec\xa3\xa0\x00\x00\x33"
    SAMPLE_LOC_RAW_1, SAMPLE_LOC_RAW_2 = SAMPLE_LOC_RAW[:35], SAMPLE_LOC_RAW[35:]
    
    # UM Example 6.1.3.4
    SAMPLE_MSG_RAW = b"\x55\x02\x19\x00\x01\x00\xef\x72\x02\x32\x01\x02\x00\x09\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\x0f"

    lt_queue.write(SAMPLE_LOC_RAW)
    lt_queue.write(SAMPLE_MSG_RAW)
    loc_decoded = lt_queue.pops(1)
    msg_decoded = lt_queue.pops(1)
    print(loc_decoded[0][0], loc_decoded[0][1].__dict__)
    print(msg_decoded[0][0], msg_decoded[0][1].__dict__)
    
    lt_queue.write(SAMPLE_LOC_RAW_1)
    print(lt_queue.pops_after(0))
    lt_queue.write(SAMPLE_LOC_RAW_2)
    print(lt_queue.pops_after(0))


if __name__ == "__main__":
    test()
