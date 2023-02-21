import cmath

rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r

class EWMF_RadialD:
    ALPHA_D, ALPHA_V = 0.3, 0.2
    READINGS_PER_MS = 0.025
    def __init__(self, d_polar):
        self.d_polar = d_polar
        self.v_polar = 0+0j
        self.d_rect = cmath.rect(d_polar.real, rad(d_polar.imag))
        self.v_rect = 0+0j

    def push(self, d_polar, dt):
        POLAR_WEIGHT = 0.5
        n_dts = self.READINGS_PER_MS * dt
        d_k = self.ALPHA_D * max(0, -(n_dts - 1) * (n_dts - 1) + 1)
        v_k = self.ALPHA_V * 0.73 * d_k
        v_polar = (d_polar - self.d_polar) / dt
        d_rect_from_polar = cmath.rect(d_polar.real, rad(d_polar.imag))
        d_rect = cmath.rect(d_polar.real, rad(d_polar.imag))
        d_rect = POLAR_WEIGHT * d_rect_from_polar + (1 - POLAR_WEIGHT) * d_rect
        v_rect = (d_rect - self.d_rect) / dt
        self.d_polar = (1 - d_k) * self.d_polar + d_k * d_polar
        self.v_polar = (1 - v_k) * self.v_polar + v_k * v_polar
        self.d_rect = (1 - d_k) * self.d_rect + d_k * d_rect
        self.v_rect = (1 - v_k) * self.v_rect + v_k * v_rect

    def trend_iter(self, n = 10, t_per_n = 20):
        d_k = self.ALPHA_D
        d_polar = self.d_polar
        d_rect = self.d_rect
        for _ in range(n):
            POLAR_WEIGHT = 0.5
            d_polar = d_polar + t_per_n * self.v_polar
            d_rect = d_rect + t_per_n * self.v_rect
            d_rect_polar_rad = cmath.polar(d_rect)
            d_rect_polar_deg = complex(d_rect_polar_rad[0], deg(d_rect_polar_rad[1]))
            yield POLAR_WEIGHT * d_polar + (1 - POLAR_WEIGHT) * d_rect_polar_deg
