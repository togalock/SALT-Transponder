import cmath
import turtle as t
from EWMF_2 import *

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
can_click = True

def onclick_timer():
    global can_click
    can_click = False
    def wrapper():
        global can_click
        can_click = True
    setTimeout(wrapper, 100)
        

def onclick_tag(x, y):
    global tag_radial, fresh_for, can_click
    if not can_click: return False
    onclick_timer()
    new_radial = complex(*cmath.polar(complex(x, y)))
    if tag_radial is None or (new_radial.real - tag_radial.d_polar.real >= 200):
        tag_radial = EWMF_RadialD(new_radial)
        fresh_for = 0
    else:
        tag_radial.push(new_radial, 40)

def tag_tick():
    global tag_radial, fresh_for
    if tag_radial:
        tag_radial.push(tag_radial.d_polar, 10)
        fresh_for += 50

    if tag_radial and fresh_for >= 5000:
        tag_radial, fresh_for = None, None


# Setup
t.tracer(0)

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
        radial_rect = cmath.rect(tag_radial.d_polar.real, tag_radial.d_polar.imag)
        x0, y0 = (radial_rect.real, radial_rect.imag)
        x0p, y0p = (tag_radial.d_rect.real, tag_radial.d_rect.imag)
        tag_dot.clear()
        tag_dot.up()
        tag_dot.color("brown")
        tag_dot.goto(x0, y0)
        tag_dot.down()
        tag_dot.dot()

        tag_dot.up()
        tag_dot.color("orange4")
        tag_dot.goto(x0p, y0p)
        tag_dot.down()
        tag_dot.dot()

        trend_dot.clear()
        trend_dot.up()
        trend_dot.goto(x0, y0)
        trend_dot.down()
        trend_dot.color("red")
        for radial in tag_radial.trend_iter(polar_weight = 0.5):
            d_rect = cmath.rect(radial.real, radial.imag)
            x, y = d_rect.real, d_rect.imag
            trend_dot.goto(x, y)
            
        trend_dot.up()
        trend_dot.goto(x0, y0)
        trend_dot.down()
        trend_dot.color("coral")
        for radial in tag_radial.trend_iter(polar_weight = 1):
            d_rect = cmath.rect(radial.real, radial.imag)
            x, y = d_rect.real, d_rect.imag
            trend_dot.goto(x, y)

        trend_dot.up()
        trend_dot.goto(x0, y0)
        trend_dot.down()
        trend_dot.color("sea green")
        for radial in tag_radial.trend_iter(polar_weight = 0):
            d_rect = cmath.rect(radial.real, radial.imag)
            x, y = d_rect.real, d_rect.imag
            trend_dot.goto(x, y)

    else:
        tag_dot.clear()
        trend_dot.clear()

    t.update()

# Main
screen = t.Screen()
t.setup(800, 600)
t.update()

setInterval(tag_tick, 100)
setInterval(draw_tag, 100)
screen.onclick(onclick_tag)

t.mainloop()

