import turtle
import cmath

rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r
px = lambda w, h: (w * turtle.window_width() // 2, h * turtle.window_height() // 2)

# See Minecraft Color Codes:
# [a-f] = [Green, Cyan, Red, Magenta, Yellow, White]
COLORS = {"a": "#55FF55", "b": "#55FFFF", "c": "#FF5555",
          "d": "#FF55FF", "e": "#FFFF55", "f": "#FFFFFF"}

def t_rect(r, a):
    d_rect = cmath.rect(r, rad(a))
    return (int(d_rect.real), int(d_rect.imag))

def setTimeout(f, t_ms):
    turtle.ontimer(f, t_ms)

def setInterval(f, t_ms):
    is_running = [True, ]
    def wrapper():
        nonlocal is_running
        if is_running[0]:
            turtle.ontimer(f, t_ms)
            turtle.ontimer(wrapper, t_ms)
            
    wrapper()
    return is_running

def Move(t: turtle.Turtle, x, y):
    t.up()
    t.goto(x, y)
    t.down()
    

def Line(t: turtle.Turtle, iterable):
    t.up()
    t.goto(*next(iterable, (0, 0)))
    t.down()
    for x, y in iterable:
        t.goto(x, y)

def CircleC(t: turtle.Turtle, x, y, r):
    t.up()
    t.seth(0)
    t.goto(x, y - r)
    t.down()
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
    t.circle(r, a2 - a1)
    if draw_r:
        t.goto(x, y)

def ArrowC(t: turtle.Turtle, x, y, r, a):
    t.up()
    t.seth(a)
    t.goto(x, y)
    t.down()
    t.fd(r)
    t.left(135)
    t.fd(r // 4)
    t.back(r // 4)
    t.left(90)
    t.fd(r // 4)
    

def RectX(t: turtle.Turtle, x1, y1, x2, y2):
    t.up()
    t.goto(x1, y1)
    t.down()
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
    t.up()
    t.goto(half_x, y1)
    t.down()
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
    #  1
    # 2^3
    p1_x = p_left * x2 + (1 - p_left) * x1
    t.up()
    t.goto(p1_x, y1)
    t.down()
    t.goto(x1, y2)
    t.goto(x2, y2)
    t.goto(p1_x, y1)

def TriUpC(t: turtle.Turtle, x, y, w, h, p_left = 0.5):
    half_w, half_h = w // 2, h // 2
    x1, y1 = x - half_w, y + half_h
    x2, y2 = x + half_w, y - half_h
    TriUpX(t, x1, y1, x2, y2, p_left)

def Text(t: turtle.Turtle, text, x1, y2,
         w=None, h=None, align="center",
         font=None, font_size=None, font_type=None,):
    WIDTH_PER_PT, HEIGHT_PER_PT = 1.008, 1.4
    DEFAULT_FONT, DEFAULT_SIZE, DEFAULT_TYPE = "JetBrains Mono", 10, "normal"
    font = font or DEFAULT_FONT
    font_size = font_size or DEFAULT_SIZE
    font_type = font_type or DEFAULT_TYPE
    if w:
        font_size = min(font_size, w / len(text) / WIDTH_PER_PT)
    if h:
        font_size = min(font_size, h / HEIGHT_PER_PT)
    t.up()
    t.goto(x1, y2)
    t.down()
    t.write(text, align=align, font=(font, font_size, font_type))
    return (len(text) * font_size * WIDTH_PER_PT,
            font_size * HEIGHT_PER_PT)