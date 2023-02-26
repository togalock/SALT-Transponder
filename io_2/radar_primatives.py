import turtle
from EWMF_2 import EWMF_RadialD
from turtle_primatives import *

SYMBOL_SIZE = px(0.05, 0.07)
CAUTION_DIST, WARNING_DIST = 1200, 600
SCALE = px(0.25, 0)[0] / WARNING_DIST # Horizontally 25% spans inner circle

def init_pen():
    turtle.Screen().setup(800, 600)
    turtle.Screen().title("SALT Base")
    turtle.Screen().bgcolor("black")
    turtle.Screen().tracer(0, 0)
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    
    return pen

def MachineTri(pen: turtle.Turtle):
    pen.color(COLORS["f"])
    TriUpC(pen, 0, 0, *SYMBOL_SIZE)

def WarningCircle(pen: turtle.Turtle):
    pen.color(COLORS["f"])
    r1, r2 = WARNING_DIST * SCALE, CAUTION_DIST * SCALE
    CircleC(pen, 0, 0, r1)
    Text(pen, str(WARNING_DIST), r1, 0)
    CircleC(pen, 0, 0, r2)
    Text(pen, str(CAUTION_DIST), r2, 0)

def WorkerBall(pen: turtle.Turtle, ewmf: EWMF_RadialD):
    if ewmf.d_polar.real < WARNING_DIST:
        pen.color(COLORS["c"])
    elif ewmf.d_polar.real < CAUTION_DIST:
        pen.color(COLORS["e"])
    else:
        pen.color(COLORS["f"])
    
    pen.begin_fill()
    worker_x, worker_y = ewmf.d_rect.real * SCALE, ewmf.d_rect.imag * SCALE
    CircleC(pen, worker_x, worker_y, SYMBOL_SIZE[0] // 2)
    pen.end_fill()
    
    Move(pen, worker_x, worker_y)
    min_rad, max_rad = 6, 0
    for d_polar in ewmf.trend_iter(n=10, dt=75000):
        min_rad, max_rad = min(min_rad, d_polar.imag), max(max_rad, d_polar.imag)
        d_rect = cmath.rect(d_polar.real, d_polar.imag)
        d_x, d_y = d_rect.real * SCALE, d_rect.imag * SCALE
        pen.goto(d_x, d_y)
    
    if ewmf.d_polar.real < WARNING_DIST:
        ArcC(pen, 0, 0, px(0.4, 0)[0], deg(min_rad) - 10, deg(max_rad) + 10, True)
