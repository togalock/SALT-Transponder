from math import sin, cos, atan
PI_INV = 0.31830988

class EWMFilter:
    # Exponential Weighted Moving Average Filter
    def __init__(self, a, v, history_size = 50):
        # a: Default Exponential Weight (Alpha)
        # v: Value (Initial)
        self.a, self.v = a, v
        self.history, self.history_size = [v] * history_size, history_size

    def push_history(self, v):
        if len(self.history) > 0:
            self.history.pop(0)
        self.history.append(v)

    def push(self, v, a = None, n = 1):
        # a: Override default alpha
        # n: Repeat n cycles
        
        if a is None: a = self.a
        self.push_history((v, a, n))
        for _ in range(n):
            self.v = (1 - a) * self.v + a * v
        return self.v

class EWMF_RadialD:
    # D_A: Difference alpha (alpha for x)
    # DD_A: Diff Diff alpha (alpha for dx/dt)
    D_A, DD_A = 0.3, 0.2
    HISTORY_SIZE = 0

    # Interval: Expected sensor refresh time (T)
    # Readings taken close to interval is more "trustable"
    
    # _I: Inverse (1/N) to speed up computation
    INTERVAL_MS, INTERVAL_MS_I = 40, 0.025

    # Rad to Deg, Deg to Rad
    RAD, RAD_INV = 57.29578, 0.0174533
        
    def __init__(self, r, a, dr = 0, da = 0, t = 0,
                 interval_ms = 100):
        self.r, self.a = (
            EWMFilter(self.D_A, r, self.HISTORY_SIZE),
            EWMFilter(self.D_A, a, self.HISTORY_SIZE))
        self.dr, self.da = (
            EWMFilter(self.DD_A, dr, self.HISTORY_SIZE),
            EWMFilter(self.DD_A, da, self.HISTORY_SIZE))
        self.t = t

        if interval_ms:
            self.INTERVAL_MS = interval_ms
            self.INTERVAL_MS_I = 1 / interval_ms

    @classmethod
    def ra_to_xy(cls, r, a):
        x, y = r * cos(a * cls.RAD_INV), r * sin(a * cls.RAD_INV)
        return (x, y)

    @classmethod
    def xy_to_ra(cls, x, y):
        r = (x * x + y * y) ** 0.5
        a = cls.RAD * atan(y / x)

        if x < 0:
            # tan works within [-90, 90];
            # Flip r instead of change heading improves \
            # trend prediction for crossing center
            r = -r
        
        return (r, a)

    @classmethod
    def certainty_by_dt(cls, a, dt):
        M = dt * cls.INTERVAL_MS_I
        
        # Certainty determined by -(x - 1)^2 + 1
        # to favor readings with dt/dt near 1;
        
        # dt/dt < 0 or dt/dt > 2 will be discarded
        A = a * -(M - 1) * (M - 1) + 1

        A = max(0, min(a, A))
        return (M, A)
        
    def push(self, r = None, a = None, t = None, dt = None):
        if dt is None:
            if t is None: return False
            (self.t, dt) = (t, t - self.t)

        _, dr_certainty = self.certainty_by_dt(self.D_A, dt)
        _, ddr_certainty = self.certainty_by_dt(self.DD_A, dt)

        r, a = self.r.v if r is None else r, self.a.v if a is None else a
        r0, a0 = self.r.v, self.a.v
        self.r.push(r, dr_certainty)
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
