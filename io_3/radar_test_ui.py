import turtle
import EWMF_2 as ewmf
import turtle_primatives as tp
import radar_primatives_2 as rp

# Test below
rp.init_screen()
pen = rp.new_pen()
# worker: ewmf.EWMF_RadialD = ewmf.EWMF_RadialD(139+2.09j, -0.0008-0.0017j)
worker = None

def draw():
    risk_meta = rp.get_risk_meta(worker)
    element_color = (tp.COLORS["c"] if risk_meta["risk_level"] >= 7 else \
                     tp.COLORS["e"] if risk_meta["risk_level"] >= 3 else \
                     tp.COLORS["f"])
    
    if risk_meta["risk_level"] >= 7:
        rp.DangerSector(pen, risk_meta["trend_sector"][0], risk_meta["trend_sector"][1])
        rp.StopBox(pen, *tp.px(-0.5, 0.8))
    
    rp.Excavator(pen)
    
    rp.RangeCircles(pen)
    rp.Worker(pen, worker, element_color)
    rp.ViewLine(pen)
    
    if risk_meta["risk_level"] >= 3:
        rp.ProximityLine(pen, worker, element_color)
    

draw()
turtle.update()