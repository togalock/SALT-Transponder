import turtle
import EWMF_2 as ewmf
import turtle_primatives as tp
import radar_primatives_2 as rp

# Test below
rp.init_screen()
pen = rp.new_pen()
worker = ewmf.EWMF_RadialD(1390+2.09j, -4-0.00017j)

def draw():
    rp.ViewLine(pen)
    rp.Excavator(pen)
    rp.RangeCircles(pen)
    rp.Worker(pen, worker)
    rp.TrendLine(pen, worker)

draw()
turtle.update()