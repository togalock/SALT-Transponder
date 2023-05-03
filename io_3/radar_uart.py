import cmath
import turtle
import asyncio

from lt_serial import get_serial_interactive
import lt_protocol as lt
import EWMF_2 as ewmf
import turtle_primatives as tp
import radar_primatives_2 as rp

lt_uart = get_serial_interactive()
lt_queue = lt.LT_Queue()
lt_nodes = lt.LT_NodeCache()

rp.init_screen()
pen = rp.new_pen()
worker, worker_time = None, None

async def uart_read():
    while True:
        lt_queue.write(lt_uart.read(500), lt.now())
        frameboxes = lt_queue.pops()
        for framebox in frameboxes:
            lt_nodes.push_framebox(framebox)
        lt_nodes.clean()
        await asyncio.sleep(0)

async def fast_forward():
    global worker, worker_time
    while True:
        if (1, 0) not in lt_nodes.nodes:
            worker, worker_time = None, 0
        else:
            worker_locs = lt_nodes.nodes[(1, 0)].locs
            if worker is None:
                worker, worker_time = ewmf.EWMF_RadialD(), lt.now()
            for _ in range(10):
                if len(worker_locs) <= 0:
                    break
                ref_time, lt_loc = worker_locs.pop(0)
                worker.push(complex(lt_loc.d, lt_loc.a + tp.rad(90)), ref_time - worker_time)
                worker_time = ref_time
        await asyncio.sleep(0)

async def draw():
    while True:
        pen.clear()
        
        if worker is not None:
            risk_meta = rp.get_risk_meta(worker)
            element_color = (tp.COLORS["c"] if risk_meta["risk_level"] >= 7 else \
                             tp.COLORS["e"] if risk_meta["risk_level"] >= 3 else \
                             tp.COLORS["f"])

            if risk_meta["risk_level"] >= 7:
                rp.BackGround(pen, tp.COLORS["g3"])
                rp.DangerSector(pen, risk_meta["trend_sector"][0], risk_meta["trend_sector"][1])
                rp.StopBox(pen, *tp.px(-0.5, 0.8))
            elif risk_meta["risk_level"] >= 1:
                rp.BackGround(pen, tp.COLORS["g2"])
        else:
            rp.BackGround(pen, tp.COLORS["g1"])
        
        rp.Excavator(pen)
        rp.RangeCircles(pen)
        
        if worker is not None:
            rp.Worker(pen, worker, element_color)
            
            # Quick Fix for Trend Lines for now
            pen.width(2)
            trend_d_rects = [cmath.rect(d_polar.real, d_polar.imag) for d_polar in risk_meta["trend_polars"]]
            trend_coords = [(c.real * rp.PX_PER_MM, c.imag * rp.PX_PER_MM) for c in trend_d_rects]
            tp.LineX(pen, trend_coords)

            # Also Quick Fix for the Arrow
            tangent_a = cmath.polar(trend_d_rects[1] - trend_d_rects[0])[1]
            tp.ArrowC(pen, worker.d_rect.real * rp.PX_PER_MM, worker.d_rect.imag * rp.PX_PER_MM,
                      tp.wpx(0.1), tp.deg(tangent_a))
            
        rp.ViewLine(pen)
        
        if worker is not None:
            if risk_meta["risk_level"] >= 3:
                rp.ProximityLine(pen, worker, element_color)

        turtle.update()
        await asyncio.sleep(0.016)


async def main():
    await asyncio.gather(uart_read(), fast_forward(), draw())

asyncio.run(main())
