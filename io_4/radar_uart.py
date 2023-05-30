import cmath
import turtle
import asyncio

from lt_serial import get_serial_interactive
import dwm_protocol as dwm
import EWMF_2 as ewmf
import turtle_primatives as tp
import radar_primatives_2 as rp

lt_uart = get_serial_interactive()
resp_queue = dwm.RESP_Queue2()

rp.init_screen()
pen = rp.new_pen()

async def uart_read():
    while True:
        resp_queue.push(lt_uart.read(800))
        for _ in range(50):
            resp_queue.pull()
            resp_queue.pull_ewmfs()
        await asyncio.sleep(0)

async def draw():
    while True:
        pen.clear()
        
        rp.BackGround(pen, tp.COLORS["g1"])
        
        rp.Excavator(pen)
        rp.RangeCircles(pen)
        
        for worker in resp_queue.ewmfs.values():
            rp.Worker(pen, worker, tp.COLORS["f"])
            
        rp.ViewLine(pen)

        turtle.update()
        await asyncio.sleep(0.016)


async def main():
    await asyncio.gather(uart_read(), draw())

asyncio.run(main())
