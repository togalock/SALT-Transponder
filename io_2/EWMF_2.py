import cmath

rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r
vdot = lambda a, b: complex(a.real * b.real, b.imag * b.imag)

class EWMF_RadialD:
    ALPHA_D = 0.4
    ALPHA_V = 0.05
    # READINGS_PER_MS = 0.025
    
    def __init__(self, d_polar, v_polar = 0+0j):
        # D_Polar: (Distance + Rad j)
        # D_Rect: (X + Y j)
        self.d_polar = d_polar
        self.v_polar = v_polar
        self.d_rect = cmath.rect(d_polar.real, d_polar.imag)
        self.v_rect = cmath.rect(v_polar.real, v_polar.imag)
    
    def __repr__(self):
        return (
            "[EWMF P%.2f∠%.2f° Δ%+.2f∠%+.2f° | R%.2f %.2f Δ%+.2f %+.2f]" % (
                self.d_polar.real, deg(self.d_polar.imag),
                self.v_polar.real, deg(self.v_polar.imag),
                self.d_rect.real, self.d_rect.imag,
                self.v_rect.real, self.v_rect.imag,
            )
        )
    
    def push(self, d_polar, dt):
        if dt <= 0: return None
        
        inv_dt = 1 / dt
        # n_dts = self.READINGS_PER_MS * dt
        
        # Parabola with (1, 1) and ((0, 0) and (2, 0)) -> [0...1]
        # to favor readings near polling rate
        # as data near polling rate is more "trustable"
        confidence = 1 # max(0, -(n_dts - 1) * (n_dts - 1) + 1)
        
        d_k = self.ALPHA_D * confidence
        v_k = self.ALPHA_V * confidence
        
        
        v_polar = (d_polar - self.d_polar) * inv_dt
        d_rect = cmath.rect(d_polar.real, d_polar.imag)
        v_rect = (d_rect - self.d_rect) * inv_dt

        self.d_polar = (1 - d_k) * self.d_polar + d_k * d_polar
        self.v_polar = (1 - v_k) * self.v_polar + v_k * v_polar
        self.d_rect = (1 - d_k) * self.d_rect + d_k * d_rect
        self.v_rect = (1 - v_k) * self.v_rect + v_k * v_rect
        
        return True

    def trend_iter(self, n = 10, dt = 20, polar_weight = 0.5):
        d_polar = self.d_polar
        d_rect = self.d_rect
        POLAR_WEIGHT = polar_weight
        for _ in range(1, n):
            # Combine polar and rectangular estimates to
            # balance between rotating machine and straight line paths
            d_polar = d_polar + dt * self.v_polar
            d_rect = d_rect + dt * self.v_rect
            d_rect_polar = complex(*cmath.polar(d_rect))
            yield POLAR_WEIGHT * d_polar + (1 - POLAR_WEIGHT) * d_rect_polar
