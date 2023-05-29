import json
import time
import EWMF_2 as ewmf

now = ewmf.now
rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r

# Units
# t (ms), d (mm), a (rad)

class RESP_Hit:
    def __init__(self, addr, d, a, ref_time = None):
        self.addr = addr
        self.d, self.a = d, a
        self.ref_time = now() if ref_time is None else ref_time
    
    def __repr__(self):
        return "<RESP_Hit %.2f ∠%.2f>" % (self.d, deg(self.a))
    
    @classmethod
    def from_dict(cls, dict_):
        try:
            if dict_["Status"] != "Ok": return False
            addr = dict_["Addr"]
            d = dict_["D_cm"] * 10
            a = rad(dict_["LPDoA_deg"] + 360)
            return cls(addr, d, a)
        except KeyError:
            return False


class RESP_Queue:
    HIT_TIMEOUT = 1000
    def __init__(self, bytes_ = b'', ewmfs = None, ref_time = None):
        self.buffer: bytearray = bytearray(bytes_)
        self.ewmfs: dict[str, ewmf.EWMF_RadialD] = ewmfs or dict()
        self.ref_time: int = now() if ref_time is None else ref_time
    
    def push(self, bytes_):
        self.buffer.extend(bytes_)
    
    def pull(self):
        sep_i = self.buffer.find(b'\r\n')
        if sep_i >= 0:
            frame, self.buffer = self.buffer[:sep_i], self.buffer[sep_i + 2:]
            try:
                dict_ = json.loads(frame)
                res = [RESP_Hit.from_dict(hit) for hit in dict_["results"]]
                return list(hit for hit in res if hit) or None
            except (KeyError, json.JSONDecodeError):
                return False
        return None
    
    def update(self, hits = list[RESP_Hit], ref_time = None):
        ref_time = now() if ref_time is None else ref_time
        for hit in hits:
            if hit.addr not in self.ewmfs or \
            ref_time - self.ewmfs[hit.addr].ref_time > self.HIT_TIMEOUT:
                self.ewmfs[hit.addr] = ewmf.EWMF_RadialD(
                    complex(hit.d, hit.a),
                    ref_time = hit.ref_time)
            else:
                self.ewmfs[hit.addr].push(complex(hit.d, hit.a), t = ref_time)
        
        for addr in self.ewmfs:
            if ref_time - self.ewmfs[addr].ref_time >= self.HIT_TIMEOUT:
                del self.ewmfs[addr]
        
        self.ref_time = ref_time


