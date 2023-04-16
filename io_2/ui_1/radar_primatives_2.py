import turtle
import cmath
import EWMF_2 as ewmf
import turtle_primatives as tp

# Unit: t (us), a (rad), d (mm)

CAUTION_DIST, WARNING_DIST = 1200, 600
SYMBOL_SIZE: tuple[float, float] = tp.px(0.05, 0.07)
PX_PER_MM: float = tp.px(0.25, 0)[0] / WARNING_DIST # Warning Circle span 25% horizontally

def init_screen():
    screen = turtle.Screen()
    screen.setup(800, 600)
    screen.title("SALT Base 4")
    screen.bgcolor(tp.COLORS["g1"])
    screen.tracer(1, 1)

def new_pen() -> turtle.Turtle:
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    return t


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
    
    point_size = tp.px(0.02, 0)[0]
    call_size = 3 * point_size
    tri_size = tp.px(0.05, 0)[0]
    
    origin: complex = PX_PER_MM * rd.d_rect
    
    trend_coords = [tp.c_tuple(PX_PER_MM * cmath.rect(d_polar.real, d_polar.imag)) for d_polar in rd.trend_iter()]
    
    # Trend Line
    t.width(1)
    t.color(element_color)
    tp.LineX(t, trend_coords)
    
    # Trend Triangle
    t.width(0)
    t.color(element_color)
    t.begin_fill()
    tp.TriPointC(t, trend_coords[0][0], trend_coords[0][1], tri_size, tp.deg(rd.v_polar.imag))
    t.end_fill()
    
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


def SafeSector(t: turtle.Turtle, a1, a2):
    safe_color = tp.COLORS["2"]
    danger_color = tp.COLORS["4"]
    
    r = tp.px(0.35, 0)[0]
    
    t.color(safe_color)
    t.begin_fill()
    tp.ArcC(t, 0, 0, r, a1, a2, draw_r=True)
    t.end_fill()
    
    t.color(danger_color)
    t.begin_fill()
    tp.ArcC(t, 0, 0, r, a2, a1, draw_r=True)
    t.end_fill()



# Test below
init_screen()
pen = new_pen()
worker = ewmf.EWMF_RadialD(1350+2.09j, -0.0003-0.0017j)

Excavator(pen)
ViewLine(pen)
RangeCircles(pen)
Worker(pen, worker)
ProximityLine(pen, worker)
SafeSector(pen, 270, 90)

turtle.update()