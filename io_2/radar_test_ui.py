import turtle
from turtle_primatives import *
from EWMF_2 import EWMF_RadialD

# Setups
turtle.setup(800, 600)
turtle.title("SALT Base")
# turtle.tracer(0, 350)
turtle.bgcolor("black")
turtle.hideturtle()

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)

symbol_size = px(0.05, 0.07)

sample_worker = EWMF_RadialD(complex(1300, rad(25)), complex(0.59, rad(-0.1)))
SCALE = px(0.25, 0)[0] / 600 # Horizontally 25% spans 60cm

def machine_triangle():
    pen.color(COLORS["f"])
    TriUpC(pen, 0, 0, *symbol_size)

def warning_circles():
    pen.color(COLORS["f"])
    r1, r2 = 600 * SCALE, 1200 * SCALE
    CircleC(pen, 0, 0, r1)
    Text(pen, "60cm", r1, 0)
    CircleC(pen, 0, 0, r2)
    Text(pen, "120cm", r2, 0)

def worker_circle(ewmf: EWMF_RadialD):
    pen.color(COLORS["f"])
    
    pen.begin_fill()
    worker_x, worker_y = ewmf.d_rect.real * SCALE, ewmf.d_rect.imag * SCALE
    CircleC(pen, worker_x, worker_y, symbol_size[0] // 2)
    pen.end_fill()
    
    Move(pen, worker_x, worker_y)
    min_rad, max_rad = 6, 0
    for d_polar in ewmf.trend_iter(n=10, dt=75):
        min_rad, max_rad = min(min_rad, d_polar.imag), max(max_rad, d_polar.imag)
        d_rect = cmath.rect(d_polar.real, d_polar.imag)
        d_x, d_y = d_rect.real * SCALE, d_rect.imag * SCALE
        pen.goto(d_x, d_y)
    ArcC(pen, 0, 0, 1500 * SCALE, deg(min_rad), deg(max_rad), True)

# Test Scripts here
machine_triangle()
warning_circles()
worker_circle(sample_worker)

turtle.mainloop()