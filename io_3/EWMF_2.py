import typing as ty
import cmath

rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r
vdot = lambda a, b: complex(a.real * b.real, b.imag * b.imag)

# Units: t (ms), a (rad), d (mm)

class EWMF_RadialD:
    ALPHA_DP, ALPHA_VP, ALPHA_VR = 0.1, 0.1, 0.003
    
    def __init__(self, d_polar = 0+0j, v_polar = 0+0j):
        # D_Polar: (Distance + Rad j)
        # D_Rect: (X + Y j)
        self.d_polar: complex = d_polar
        self.v_polar: complex = v_polar
        self.d_rect: complex = cmath.rect(d_polar.real, d_polar.imag)
        self.v_rect: complex = cmath.rect(v_polar.real, v_polar.imag)
    
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
        if dt <= 0:
            return False

        dp_k = self.ALPHA_DP
        vp_k = self.ALPHA_VP
        vr_k = self.ALPHA_VR

        d_rect = cmath.rect(d_polar.real, d_polar.imag)
        v_polar = (d_polar - self.d_polar) / dt
        v_rect = (d_rect - self.d_rect) / dt

        self.d_polar = (1 - dp_k) * self.d_polar + dp_k * d_polar
        # Matching DP and DR reduces R alignment drift causing RV fluctuations
        self.d_rect = cmath.rect(self.d_polar.real, self.d_polar.imag)
        self.v_polar = (1 - vp_k) * self.v_polar + vp_k * v_polar
        self.v_rect = (1 - vr_k) * self.v_rect + vr_k * v_rect
        
        return (self.d_polar, self.d_rect, self.v_polar, self.v_rect)

    def trend_iter(self, n = 5, dt = 100, polar_weight = 0.5) -> ty.Iterator[complex]:
        # Returns D_Polars
        d_polar = self.d_polar
        d_rect = self.d_rect
        POLAR_WEIGHT = polar_weight
        
        # Include current position in prediction for continuous lines
        yield d_polar
        
        for _ in range(n):
            # Combine polar and rectangular estimates to
            # balance between rotating machine and straight line paths
            d_polar = d_polar + dt * self.v_polar
            d_rect = d_rect + dt * self.v_rect
            d_rect_polar = complex(*cmath.polar(d_rect))
            yield POLAR_WEIGHT * d_polar + (1 - POLAR_WEIGHT) * d_rect_polar
