import json
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
            a = rad(dict_["LAoA_deg"])
            return cls(addr, d, a)
        except KeyError:
            return False

class RESP_Queue2:
    HIT_TIMEOUT = 100000
    def __init__(self,
                 buffer = b'', hits = None, ewmfs = None,
                 ref_time = None):
        self.buffer: bytearray = bytearray(buffer)
        self.hits: dict[str, dict[int, RESP_Hit]] = hits if hits is not None else dict()
        self.ewmfs: dict[str, ewmf.EWMF_RadialD] = ewmfs if ewmfs is not None else dict()
        self.ref_time = now() if ref_time is None else ref_time
    
    def push(self, bytes_):
        self.buffer.extend(bytes_.strip(b'\x00'))
    
    def pull(self):
        self.buffer = self.buffer.strip(b'\x00')
        sep_i = self.buffer.find(b'\r\n')
        if sep_i >= 0:
            frame, self.buffer = self.buffer[:sep_i], self.buffer[sep_i + 2:]
            try:
                dict_ = json.loads(frame)
                board_id = dict_["id"]
                for data in dict_["results"]:
                    hit = RESP_Hit.from_dict(data)
                    if hit:
                        self.hits[hit.addr] = self.hits.get(hit.addr, dict())
                        self.hits[hit.addr][board_id] = hit

            except (KeyError, json.JSONDecodeError):
                return False

        return self.hits
    
    def get_hits(self, ref_time = None) -> dict[str, RESP_Hit]:
        ref_time = now() if ref_time is None else ref_time
        hits: dict[str, RESP_Hit] = dict()
        for addr in self.hits:
            hit_chosen = (None, None)
            for board_id, board_hit in self.hits[addr].items():
                if ref_time - board_hit.ref_time >= self.HIT_TIMEOUT:
                    continue
                hit_chosen = (board_id, board_hit) if hit_chosen[1] is None else \
                            (board_id, board_hit) if board_hit.a < hit_chosen[1].a else \
                            hit_chosen
            if hit_chosen[1] is not None:
                angle_offset = {1: 90, 2: 210, 3: 330}
                actual_angle = rad((angle_offset.get(hit_chosen[0], 0) - deg(hit_chosen[1].a)) % 360)
                hit_chosen[1].a = actual_angle
                hits[addr] = hit_chosen[1]
        
        return hits
    
    def pull_ewmfs(self, ref_time = None):
        ref_time = now() if ref_time is None else ref_time
        hits = self.get_hits()
        for addr in hits:
            if addr not in self.ewmfs or ref_time - self.ewmfs[addr].ref_time >= self.HIT_TIMEOUT:
                self.ewmfs[addr] = ewmf.EWMF_RadialD(complex(hits[addr].d, hits[addr].a))
            else:
                self.ewmfs[addr].push(complex(hits[addr].d, hits[addr].a), t = ref_time)
        
        return self.ewmfs

# Obsolete - Reference Implementation
class RESP_Queue:
    HIT_TIMEOUT = 1000
    def __init__(self, buffer = b'', ewmfs = None, ref_time = None):
        self.buffer: bytearray = bytearray(buffer)
        self.ewmfs: dict[str, ewmf.EWMF_RadialD] = ewmfs or dict()
        self.ref_time: int = now() if ref_time is None else ref_time
    
    def push(self, bytes_):
        self.buffer.extend(bytes_.strip(b'\x00'))
    
    def pull(self):
        self.buffer = self.buffer.strip(b'\x00')
        sep_i = self.buffer.find(b'\r\n')
        if sep_i >= 0:
            frame, self.buffer = self.buffer[:sep_i], self.buffer[sep_i + 2:]
            try:
                dict_ = json.loads(frame)
                res = [RESP_Hit.from_dict(hit)
                       for hit in dict_["results"]]
                return list(hit for hit in res if hit) or None
            except (KeyError, json.JSONDecodeError):
                return False
        return None
    
    def update(self, hits: list[RESP_Hit], ref_time = None):
        ref_time = now() if ref_time is None else ref_time
        for hit in hits:
            if hit.addr not in self.ewmfs or \
            ref_time - self.ewmfs[hit.addr].ref_time > self.HIT_TIMEOUT:
                self.ewmfs[hit.addr] = ewmf.EWMF_RadialD(
                    complex(hit.d, hit.a), ref_time = hit.ref_time)
            else:
                self.ewmfs[hit.addr].push(complex(hit.d, hit.a), t = ref_time)

        expired_addrs = [addr for addr in self.ewmfs \
                         if ref_time - self.ewmfs[addr].ref_time >= self.HIT_TIMEOUT]
        for addr in expired_addrs:
            del self.ewmfs[addr]
        
        self.ref_time = ref_time
