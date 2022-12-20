from math import sin, cos, atan
import turtle as t
from EWMF_Filter import *
import lt_uart
from time import sleep

def rotate_m90(x, y):
    return (-y, x)

def rotate_90(x, y):
    return (y, -x)

def setTimeout(f, t_ms):
    t.ontimer(f, t_ms)

def setInterval(f, t_ms):
    is_running = [True, ]
    def wrapper():
        nonlocal is_running
        if is_running[0]:
            f()
            t.ontimer(wrapper, t_ms)
            
    wrapper()
    return is_running

ADDR = "/dev/cu.usbmodem542A0368641"
lt_uart = lt_uart.LT_UART(ADDR, 115200, timeout = 0.000001)
tag_radial, disappear_timeout = None, 0
last_lt_loc, last_lt_time = None, None
drop_frame_coolout = 2

def tag_tick():
    global tag_radial, disappear_timeout, drop_frame_coolout, \
           last_lt_loc, lt_uart
    
    last_frame = None
    
    for _ in range(drop_frame_coolout):
        last_frame = lt_uart.poll_frame(160) or last_frame
        
    if not last_frame:
        last_lt_loc = None
    
    else:
        last_lt_loc = last_frame[0].data[0][1] \
                      if last_frame and len(last_frame[0].data) \
                      else None
        last_lt_time = last_frame[0].of_time[0]
    
    if disappear_timeout >= 2500:
        tag_radial = None
        disappear_timeout = 0
        return None

    if last_lt_loc is None:
        disappear_timeout = min(2500, disappear_timeout + 5)
        return None
    
    disappear_timeout = 0
    
    r, a = last_lt_loc.d * 120, last_lt_loc.a
    t = last_lt_time

    if tag_radial is None:
        tag_radial = EWMF_RadialD(r, a, t = t)
    else:
        tag_radial.push(r, a, t)

# Setup
t.tracer(0)

# Machine
m_arrow = t.Turtle()
m_arrow.color("white")
m_arrow.speed(0)
m_arrow.left(90)
m_arrow.shapesize(2, 2)

# Tag
tag_dot = t.Turtle()
tag_dot.speed(0)
tag_dot.width(10)
tag_dot.hideturtle()

trend_dot = t.Turtle()
trend_dot.speed(0)
trend_dot.color("lavender")
trend_dot.width(5)
trend_dot.hideturtle()

danger_arc = t.Turtle()
danger_arc.speed(0)
danger_arc.color("red")
danger_arc.hideturtle()

safe_arc = t.Turtle()
safe_arc.speed(0)
safe_arc.color("green")
safe_arc.hideturtle()

def draw_tag():
    global tag_radial, disappear_timeout

    danger_arc.clear()
    safe_arc.clear()
    
    if tag_radial:
        x0, y0 = EWMF_RadialD.ra_to_xy(tag_radial.r.v, tag_radial.a.v)
        x0, y0 = rotate_m90(x0, y0)
        tag_dot.clear()
        tag_dot.up()
        tag_dot.goto(x0, y0)
        tag_dot.down()

        if disappear_timeout > 200:
            tag_dot.color("grey")
        elif tag_radial.r.v < 75:
            tag_dot.color("red")
        elif tag_radial.r.v < 150:
            tag_dot.color("orange")
        else:
            tag_dot.color("lightcyan")
            
        tag_dot.dot()

        trend_dot.clear()
        trend_dot.up()
        trend_dot.goto(x0, y0)
        trend_dot.down()

        min_r, min_a, max_a = 1000, 0, 0

        for (r, a) in tag_radial.trend_iter(5000, 5):
            if disappear_timeout > 200:
                trend_dot.color("grey")
            elif r < 75:
                trend_dot.color("red")
            elif r < 150:
                trend_dot.color("orange")
            else:
                trend_dot.color("lightcyan")

            min_r = min(min_r, r)
            min_a, max_a = min(min_a, a), max(max_a, a)
            
            x, y = EWMF_RadialD.ra_to_xy(r, a)
            trend_dot.goto(*rotate_m90(x, y))
        
    else:
        tag_dot.clear()
        trend_dot.clear()

    t.update()

# Setup
screen = t.Screen()
t.setup(800, 600)
t.bgcolor("black")

# Circles
warning_circle = t.Turtle()
warning_circle.speed(0)
warning_circle.hideturtle()

warning_circle.color("yellow")
warning_circle.dot(300)
warning_circle.dot(300 - 3, t.bgcolor())

warning_circle.color("red")
warning_circle.dot(150)
warning_circle.dot(150 - 3, t.bgcolor())

# Main
t.update()

setInterval(tag_tick, 1)
setInterval(draw_tag, 1)

t.delay(0.001)

t.mainloop()
