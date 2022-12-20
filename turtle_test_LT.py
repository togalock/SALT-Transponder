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
lt_uart = lt_uart.LT_UART(ADDR, 115200, timeout = 0.0001)
tag_radial, disappear_timeout = None, 0
last_lt_loc, last_lt_time = None, None
drop_frame_coolout = 0

def tag_tick():
    global tag_radial, disappear_timeout, drop_frame_coolout,\
           last_frame, lt_uart
    last_frame = lt_uart.poll_frame(500)
    
    if not last_frame:
        last_lt_loc = None
    else:
        if drop_frame_coolout > 0:
            drop_frame_coolout -= 3
            last_lt_loc = None
            return None

        print(drop_frame_coolout)
        drop_frame_coolout = 1
        last_lt_loc = last_frame[0].data[0][1] \
                      if last_frame and len(last_frame[0].data) \
                      else None
        last_lt_time = last_frame[0].of_time[0]
    
    if disappear_timeout >= 2500:
        tag_radial = None
        return None

    if last_lt_loc is None:
        disappear_timeout = min(500, disappear_timeout + 50)
        return None

    disappear_timeout = 0
    r, a = last_lt_loc.d * 1000, last_lt_loc.a
    t = last_lt_time

    if tag_radial is None:
        tag_radial = EWMF_RadialD(r, a, t = t)
    else:
        tag_radial.push(r, a, t)

# Setup
t.tracer(0)

# Machine
m_arrow = t.Turtle()
m_arrow.speed(0)
m_arrow.left(90)
m_arrow.shapesize(2, 2)

# Tag
tag_dot = t.Turtle()
tag_dot.speed(0)
tag_dot.color("brown")
tag_dot.width(10)
tag_dot.hideturtle()

trend_dot = t.Turtle()
trend_dot.speed(0)
trend_dot.color("red")
trend_dot.width(5)
trend_dot.hideturtle()

def draw_tag():
    global tag_radial, fresh_for
    
    if tag_radial:
        x0, y0 = EWMF_RadialD.ra_to_xy(tag_radial.r.v, tag_radial.a.v)
        x0, y0 = rotate_m90(x0, y0)
        tag_dot.clear()
        tag_dot.up()
        tag_dot.goto(x0, y0)
        tag_dot.down()
        tag_dot.dot()

        trend_dot.clear()
        trend_dot.up()
        trend_dot.goto(x0, y0)
        trend_dot.down()
        for (r, a) in tag_radial.trend_iter(2000, 3):
            x, y = EWMF_RadialD.ra_to_xy(r, a)
            trend_dot.goto(*rotate_m90(x, y))
    
    else:
        tag_dot.clear()
        trend_dot.clear()

    t.update()

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
screen = t.Screen()
t.setup(800, 600)
t.update()

setInterval(tag_tick, 20)
setInterval(draw_tag, 50)

t.mainloop()
