import turtle
import cmath
import EWMF_2 as ewmf
import turtle_primatives as tp

# Helper Functions
rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r
c_tuple = lambda c: (c.real, c.imag)

# Unit: t (ms), a (rad), d (mm)
# Constant Definitions
CAUTION_DIST, WARNING_DIST = 1200, 600
SYMBOL_SIZE: float = min(tp.px(0.02, 0.02))
PX_PER_MM: float = tp.px(0.25, 0)[0] / WARNING_DIST # Warning Circle span 25% horizontally

# Initialization
def init_screen():
    screen = turtle.Screen()
    screen.setup(800, 600)
    screen.title("SALT Base 4")
    screen.bgcolor(tp.COLORS["g1"])
    screen.tracer(0, 0)

def new_pen() -> turtle.Turtle:
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    return t

# Graphic Elements
def BackGround(t: turtle.Turtle, color):
    t.color(color)
    t.begin_fill()
    tp.RectX(t, *tp.px(-1, 1), *tp.px(1, -1))
    t.end_fill()

def Excavator(t: turtle.Turtle):
    exca_size = tp.px(0.09, 0.15)
    wheel_size = (exca_size[0] // 4, exca_size[1] * 1.2)
    cabin_size = (exca_size[0] // 3, exca_size[1] // 3)
    arm_size = (exca_size[0] // 3, exca_size[1])
    
    # Wheels
    t.color(tp.COLORS["0"])
    t.begin_fill()
    tp.RectC(t, exca_size[0] // 2, 0, wheel_size[0], wheel_size[1])
    t.end_fill()
    
    t.begin_fill()
    tp.RectC(t, -exca_size[0] // 2, 0, wheel_size[0], wheel_size[1])
    t.end_fill()
    
    # Body
    t.color(tp.COLORS["0"], tp.COLORS["6"])
    t.begin_fill()
    tp.RectC(t, 0, 0, exca_size[0], exca_size[1])
    t.end_fill()
    
    # Cabin
    t.color(tp.COLORS["f"])
    t.begin_fill()
    tp.RectC(t, -exca_size[0] // 4, exca_size[1] // 4, cabin_size[0], cabin_size[1])
    t.end_fill()
    
    # Arm
    t.color(tp.COLORS["0"], tp.COLORS["6"])
    t.begin_fill()
    tp.RectC(t, 0, exca_size[1] // 2, arm_size[0], arm_size[1])
    t.end_fill()


def RangeCircles(t: turtle.Turtle):
    caution_radius = CAUTION_DIST * PX_PER_MM
    warning_radius = WARNING_DIST * PX_PER_MM
    
    caution_text = str(CAUTION_DIST)
    warning_text = str(WARNING_DIST)
    
    text_color = tp.COLORS["8"]
    caution_color = tp.COLORS["e"]
    warning_color = tp.COLORS["c"]
    
    t.color(warning_color)
    tp.CircleC(t, 0, 0, warning_radius)
    t.color(text_color)
    tp.Text(t, warning_text, warning_radius, 0)
    
    t.color(caution_color)
    tp.CircleC(t, 0, 0, caution_radius)
    t.color(text_color)
    tp.Text(t, caution_text, caution_radius, 0)


def ViewLine(t: turtle.Turtle):
    r = tp.px(0, 2)[1]
    t.color(tp.COLORS["f"])
    
    tp.LineC(t, 0, 0, r, 60)
    tp.LineC(t, 0, 0, r, 120)


def Worker(t: turtle.Turtle, rd: ewmf.EWMF_RadialD,
                  element_color = tp.COLORS["f"],
                  is_selected = False, is_called = False):
    select_color = tp.COLORS["b"]
    call_color = tp.COLORS["f"]
    
    point_size = SYMBOL_SIZE
    call_size = 3 * point_size
    
    origin: complex = PX_PER_MM * rd.d_rect
    
    # Call Rectangle
    if is_called:
        t.width(2)
        t.color(call_color)
        tp.RectC(t, origin.real, origin.imag, call_size, call_size)
    
    # Dot
    t.width(3 if is_selected else 0)
    t.color(select_color if is_selected else element_color, element_color)
    t.begin_fill()
    tp.CircleC(t, origin.real, origin.imag, point_size)
    t.end_fill()

def TrendLine(t: turtle.Turtle, rd: ewmf.EWMF_RadialD,
              width = 1, element_color = tp.COLORS["f"]):
    t.width(width)
    t.color(element_color)
    
    origin: complex = rd.d_rect * PX_PER_MM
    
    trend_heading = deg(cmath.polar(rd.v_rect)[1])
    trend_origin = tp.CoordXC(origin.real, origin.imag, SYMBOL_SIZE * 1.1, trend_heading)
    tp.TriPointC(t, trend_origin[0], trend_origin[1], SYMBOL_SIZE, trend_heading)
    
    trend_points = (
        c_tuple(cmath.rect(trend_rd.real, trend_rd.imag) * PX_PER_MM)
        for trend_rd in rd.trend_iter())
    tp.LineX(t, trend_points)

def ProximityLine(t: turtle.Turtle, rd: ewmf.EWMF_RadialD,
                  element_color = tp.COLORS["e"]):
    proximity_text = "%i" % (rd.d_polar.real)
    
    r = PX_PER_MM * rd.d_polar.real
    text_origin = tp.c_tuple(cmath.rect(r // 2, rd.d_polar.imag + tp.rad(10)))
    
    t.width(3)
    t.color(element_color)
    tp.DashedLineC(t, 0, 0, r, tp.deg(rd.d_polar.imag))
    
    t.color(element_color)
    tp.Text(t, proximity_text, text_origin[0], text_origin[1])


def DangerSector(t: turtle.Turtle, a1, a2):
    safe_color = tp.COLORS["2"]
    danger_color = tp.COLORS["4"]
    
    r = tp.px(0.35, 0)[0]
    
    t.color(danger_color)
    t.begin_fill()
    tp.ArcC(t, 0, 0, r, a1, a2, draw_r=True)
    t.end_fill()
    
    t.color(safe_color)
    t.begin_fill()
    tp.ArcC(t, 0, 0, r, a2, a1, draw_r=True)
    t.end_fill()
    

def StopBox(t: turtle.Turtle, x, y):
    box_color = tp.COLORS["c"]
    text_color = tp.COLORS["c"]
    stop_text = "> STOP <"
    
    _, text_bound = tp.TextBounds(stop_text, font_size=20)
    
    t.width(3)
    t.color(box_color)
    tp.RectC(t, x, y, text_bound[0], text_bound[1])
    
    t.color(text_color)
    tp.Text(t, stop_text, x, y - text_bound[1] // 2, font_size=20)

# Logic Elements
def get_risk_meta(rd: ewmf.EWMF_RadialD):
    trend_iter = rd.trend_iter()
    trend_polars = [d_polar for d_polar in trend_iter]
    trend_bearings = [deg(d_polar.imag) for d_polar in trend_polars]
    trend_radiuses = [d_polar.real for d_polar in trend_polars]
    
    trend_r_1s = min(trend_radiuses[:5])
    trend_r_2s = min(trend_radiuses)
    trend_sector = (min(trend_bearings) - 30, max(trend_bearings) + 30)
    
    risk_level = 0
    if trend_r_1s <= WARNING_DIST or rd.d_polar.real <= WARNING_DIST:
        risk_level = 7
        
    elif trend_r_1s <= CAUTION_DIST:
        risk_level = 3
        
    elif rd.d_polar.real <= CAUTION_DIST:
        risk_level = 2
    
    else:
        pass
    
    res = {
        "trend_polars": trend_polars,
        "trend_radiuses": trend_radiuses,
        "trend_bearings": trend_bearings,
        "trend_sector": trend_sector,
        "risk_level": risk_level,
    }
    
    return res