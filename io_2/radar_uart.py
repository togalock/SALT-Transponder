import turtle

from lt_serial import get_serial_interactive
import lt_protocol as lt
from EWMF_2 import EWMF_RadialD
from turtle_primatives import *
from radar_components import *

MS = 1000
MAX_WORKER_LIFE = 2000 * MS

lt_uart = get_serial_interactive()
lt_queue = lt.LTQueue()
system_time = lt.now()
worker, worker_last_seen = None, None
is_ffing = True

pen = init_pen()

def uart_read():
    lt_queue.write(lt_uart.read(500), lt.now())

def fast_forward(t = 30, step = 1):
    global worker, worker_last_seen, system_time, is_ffing
    frame_queue = lt_queue.pops_after(system_time + t)
    frame_queue = frame_queue[::step]
    system_time = lt.now()
    for time, lt_locs in frame_queue:
        if lt_locs is not None and lt_locs.n_nodes >= 1: # If tag is present
            new_d_polar = complex(lt_locs.lt_locs[0].d, lt_locs.lt_locs[0].a + rad(90))
            if worker is None:
                worker = EWMF_RadialD(new_d_polar)
            else:
                dt = time - worker_last_seen
                worker.push(new_d_polar, dt)
            worker_last_seen = time
        else:
            if worker and time - worker_last_seen >= MAX_WORKER_LIFE:
                worker, worker_last_seen = None, None

    is_ffing = not(is_ffing)

def draw():
    pen.clear()
    MachineTri(pen)
    WarningCircle(pen)
    if worker is not None: WorkerBall(pen, worker)
    FFSquare(pen, is_ffing)
    turtle.Screen().update()

setInterval(uart_read, 1)
setInterval(fast_forward, 3)
setInterval(draw, 10)

turtle.mainloop()
