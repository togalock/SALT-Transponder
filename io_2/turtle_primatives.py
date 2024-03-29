import typing as ty
import turtle
import cmath

rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r
px = lambda w, h: (w * turtle.window_width() // 2, h * turtle.window_height() // 2)
hpx = lambda h: h * turtle.window_height() // 2
wpx = lambda w: w * turtle.window_width() // 2
c_tuple = lambda c: (c.real, c.imag)

# See Minecraft Color Codes:
# [a-f] = [Green, Cyan, Red, Magenta, Yellow, White]
# [g1-g3] = Ground Shades, Lightest -> Darkest
COLORS = {
    "0": "#000000",
    "1": "#0000AA", "2": "#00AA00", "3": "#00AAAA",
    "4": "#AA0000", "5": "#AA00AA", "6": "#FFAA00",
    "7": "AAAAAA", "8": "#555555", "9": "#5555FF",
    "a": "#55FF55", "b": "#55FFFF", "c": "#FF5555",
    "d": "#FF55FF", "e": "#FFFF55", "f": "#FFFFFF",
    "g1": "#CC9933", "g2": "#996600", "g3": "#660000",
    }

class Callback:
    # This class prevents RecursionError by
    # inhibiting Interval Callbacks from scheduling itself
    # before it has run at least once.
    def __init__(self, f, t_ms, is_interval = False, start_now = True):
        self.f, self.t_ms = f, t_ms
        self.is_interval = is_interval
        self.has_run = False
        self.is_active = True
        if start_now:
            turtle.ontimer(self, self.t_ms)

    def __call__(self):
        if not self.is_active: return False
        if not self.has_run:
            res = self.f()
            self.has_run = True
        if self.is_interval and self.has_run:
            turtle.ontimer(self, self.t_ms)
        return res
    
    def start(self):
        if not self.is_interval:
            self.has_run = False
        self.is_active = True
    
    def stop(self):
        self.is_active = False

# Functions remains for compatibility purposes
# To be Deprecated
def setTimeout(f, t_ms):
    return Callback(f, t_ms)

def setInterval(f, t_ms):
    return Callback(f, t_ms, True)

# Affix for All Graphical Components:
# X: Receives Origin x, y, width and height
# C: Receives Origin x, y, radius and angle
def Move(t: turtle.Turtle, x, y):
    t.up()
    t.goto(x, y)
    t.down()


def LineX(t: turtle.Turtle, iterator: ty.Iterator[tuple[int, int]]):
    iterator = iter(iterator) if hasattr(iterator, "__iter__") else iterator
    Move(t, *next(iterator, (0, 0)))
    for x, y in iterator:
        t.goto(x, y)


def LineC(t: turtle.Turtle, x, y, r, a):
    Move(t, x, y)
    t.seth(a)
    t.fd(r)


def DashedLineX(t: turtle.Turtle,
                iterator: ty.Iterator[tuple[int, int]],
                parts = 5):
    iterator = iter(iterator) if hasattr(iterator, "__iter__") else iterator
    fragments = parts * 2
    Move(t, *next(iterator, (0, 0)))
    for x, y in iterator:
        origin_steps = ((complex(x, y) - complex(*turtle.pos())) // fragments)
        step_x, step_y = origin_steps.real, origin_steps.imag
        for fragment in range(fragments):
            if fragment % 2:
                t.down()
            else:
                t.up()
            t.goto(fragment * step_x, fragment * step_y)


def DashedLineC(t: turtle.Turtle, x, y, r, a,
                parts = 5):
    fragments = parts * 2
    step_r = r / fragments
    Move(t, x, y)
    t.seth(a)
    for fragment in range(fragments):
        if fragment % 2:
            t.down()
        else:
            t.up()
        t.fd(step_r)


def CircleC(t: turtle.Turtle, x, y, r):
    Move(t, x, y - r)
    t.seth(0)
    t.circle(r)


def ArcC(t: turtle.Turtle, x, y, r, a1, a2, draw_r = False):
    t.up()
    t.goto(x, y)
    t.seth(a1)
    if draw_r:
        t.down()
    t.fd(r)
    t.left(90)
    t.down()
    t.circle(r, (a2 - a1 + 360) % 360)
    if draw_r:
        t.goto(x, y)


def ArrowC(t: turtle.Turtle, x, y, r, a):
    Move(t, x, y)
    t.seth(a)
    t.fd(r)
    t.left(135)
    t.fd(r // 4)
    t.back(r // 4)
    t.left(90)
    t.fd(r // 4)
    

def RectX(t: turtle.Turtle, x1, y1, x2, y2):
    Move(t, x1, y1)
    t.goto(x2, y1)
    t.goto(x2, y2)
    t.goto(x1, y2)
    t.goto(x1, y1)


def RectC(t: turtle.Turtle, x, y, w, h):
    half_w, half_h = w // 2, h // 2
    x1, x2 = x - half_w, x + half_w
    y1, y2 = y + half_h, y - half_h
    RectX(t, x1, y1, x2, y2)


def DiamondX(t: turtle.Turtle, x1, y1, x2, y2):
    half_x, half_y = (x1 + x2) // 2, (y1 + y2) // 2
    Move(t, half_x, y1)
    t.goto(x2, half_y)
    t.goto(half_x, y2)
    t.goto(x1, half_y)
    t.goto(half_x, y1)


def DiamondC(t: turtle.Turtle, x, y, w, h):
    half_w, half_h = w // 2, h // 2
    x1, y1 = x - half_w, y + half_h
    x2, y2 = x + half_w, y - half_h
    DiamondX(t, x1, y1, x2, y2)


def TriUpX(t: turtle.Turtle, x1, y1, x2, y2, p_left = 0.5):
    # p_left indicates middle point ratio along 2-3
    #  1
    # 2^3
    p1_x = p_left * x2 + (1 - p_left) * x1
    Move(t, p1_x, y1)
    t.goto(x1, y2)
    t.goto(x2, y2)
    t.goto(p1_x, y1)


def TriUpC(t: turtle.Turtle, x, y, w, h, p_left = 0.5):
    half_w, half_h = w // 2, h // 2
    x1, y1 = x - half_w, y + half_h
    x2, y2 = x + half_w, y - half_h
    TriUpX(t, x1, y1, x2, y2, p_left)


def TriPointC(t: turtle.Turtle, x, y, r, a, p_y = 0.5):
    # Isosceles triangle along a radial
    # p_y indicates height to width ratio
    v1 = cmath.rect(r, rad(a)) + complex(x, y)
    v2 = cmath.rect(p_y * 0.5 * r, rad(a + 90)) + complex(x, y)
    v3 = cmath.rect(p_y * 0.5 * r, rad(a - 90)) + complex(x, y)
    x1, y1, x2, y2, x3, y3 = v1.real, v1.imag, v2.real, v2.imag, v3.real, v3.imag
    Move(t, x1, y1)
    t.goto(x2, y2)
    t.goto(x3, y3)
    t.goto(x1, y1)
    

def TextBounds(text, w=None, h=None, font_size=10) -> tuple[int, int, int]:
    WIDTH_PER_PT, HEIGHT_PER_PT = 1.1, 1.5
    if w: font_size = min(font_size, w / len(text) / WIDTH_PER_PT)
    if h: font_size = min(font_size, h / HEIGHT_PER_PT)
    return (font_size, len(text) * font_size * WIDTH_PER_PT, font_size * HEIGHT_PER_PT)


def Text(t: turtle.Turtle, text, x1, y2,
         w=None, h=None, align="center",
         font="B612 Mono", font_size=10, font_type="normal",):
    font_size = TextBounds(text, w, h, font_size)[0]
    t.up()
    t.goto(x1, y2)
    t.down()
    t.write(text, align=align, font=(font, font_size, font_type))