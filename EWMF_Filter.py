class EWMFilter:
    def __init__(self, a, v, history_size = 50):
        self.a, self.v = a, v
        self.history, self.history_size = [v] * history_size, history_size

    def push_history(self, v):
        if len(self.history) > 0:
            self.history.pop(0)
        self.history.append(v)

    def push(self, v, a = None, n = 1):
        if a is None: a = self.a
        self.push_history((v, a, n))
        for _ in range(n):
            self.v = (1 - a) * self.v + a * v
        return self.v

class EWMF_RadialD:
    D_A, DD_A = 0.3, 0.2
    HISTORY_SIZE = 50
    INTERVAL_MS, INTERVAL_MS_I = 400, 0.0025
    
    def __init__(self, r, a, dr = 0, da = 0, t = 0):
        self.r, self.a = (
            EWMFilter(D_A, r, HISTORY_SIZE),
            EWMFilter(D_A, a, HISTORY_SIZE))
        self.dr, self.da = (
            EWMFilter(DD_A, dr, HISTORY_SIZE),
            EWMFilter(DD_A, da))
        self.t = t

    @classmethod
    def certainty_by_dt(cls, a, dt):
        M = dt * cls.INTERVAL_MS_I
        A = a / (M * M)
        return (M, A)
        
    def push(r = None, a = None, t = None, dt = None):
        if dt is None:
            if t is None: return False
            (self.t, dt) = (t, t - self.t)

        _, DR_M_I, dr_certainty = self.certainty_by_dt(D_A, dt)
        _, DDR_M_I, ddr_certainty = self.certainty_by_dt(DD_A, dt)

        r0, a0 = self.r.v, self.a.v
        self.r.push(v, dr_certainty)
        self.a.push(a, dr_certainty)

        self.dr.push((r - r0) / dt, ddr_certainty)
        self.da.push((a - a0) / dt, ddr_certainty)

    def trend_iter(self, t_ms = 100, n = 10):
        r, a = self.r.v, self.a.v
        dr, da = self.dr.v, self.da.v
        M = t_ms * self.INTERVAL_MS_I
        for _ in range(n):
            r, a = r + M * dr, a + M * da
            yield (r, a)
        return None
