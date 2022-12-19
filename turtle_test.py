from math import sin, cos, atan
import turtle as t
from EWMF_Filter import *

def setTimeout(f, t_ms):
    t.ontimer(f, t_ms)

def setInterval(f, t_ms):
    is_running = [True, ]
    def wrapper():
        nonlocal is_running
        if is_running[0]:
            t.ontimer(f, t_ms)
            t.ontimer(wrapper, t_ms)
            
    wrapper()
    return is_running

tag_radial, fresh_for = None, None
click_cooldown = 0

def click_tick():
    global click_cooldown
    click_cooldown = max(0, click_cooldown - 100)

def onclick_tag(x, y):
    global tag_radial, fresh_for, click_cooldown
    if click_cooldown <= 0:
        click_cooldown += 100
        r, a = EWMF_RadialD.xy_to_ra(x, y)
        if tag_radial is None \
           or abs(tag_radial.r.v - r) >= 150:
            tag_radial = EWMF_RadialD(r, a)
            fresh_for = 0

        else:
            tag_radial.push(r, a, dt = 100)
            fresh_for = 0

def tag_tick():
    global tag_radial, fresh_for
    if tag_radial:
        tag_radial.push(dt = 100)
        fresh_for += 50

    if tag_radial and fresh_for >= 5000:
        tag_radial, fresh_for = None, None

# Setup
m_arrow = t.Turtle()
m_arrow.speed(0)
m_arrow.shapesize(2, 2)

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
        
        tag_dot.clear()
        tag_dot.up()
        tag_dot.goto(x0, y0)
        tag_dot.down()
        tag_dot.dot()

        trend_dot.clear()
        trend_dot.up()
        trend_dot.goto(x0, y0)
        trend_dot.down()
        for (r, a) in tag_radial.trend_iter(2000, 10):
            x, y = EWMF_RadialD.ra_to_xy(r, a)
            trend_dot.goto(x, y)

    else:
        tag_dot.clear()
        trend_dot.clear()

    t.update()

screen = t.Screen()
t.setup(800, 600)
setInterval(tag_tick, 100)
setInterval(draw_tag, 100)
setInterval(click_tick, 100)
screen.onclick(onclick_tag)

t.tracer(0)

try:
    t.mainloop()
except:
    t.bye()
