import turtle

rad = lambda d: 0.0174533 * d
deg = lambda r: 57.29578 * r

def Circle(t: turtle.Turtle, x, y, r):
    t.up()
    t.seth(0)
    t.goto(x, y - r)
    t.down()
    t.circle(r)

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
    pass

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