# main.py - Beispiel fuer ws2812_parallel_async.py
import uasyncio as asyncio
from libs.ws2812_parallel_async import WS2812ParallelAsync

COLOURS = (
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (0, 255, 255), (255, 0, 255), (255, 128, 0), (255, 255, 255),
)

async def heartbeat():
    # Platzhalter fuer weitere Tasks, Sensoren, Kommunikation usw.
    while True:
        await asyncio.sleep_ms(1000)

async def animation(leds):
    pos = 0
    while True:
        # copy=False ist optimal, weil dieser Frame komplett neu aufgebaut wird.
        leds.clear()
        for ch in range(8):
            leds.pixel(ch, (pos + ch * 11) % leds.leds, COLOURS[ch])

        # Kodiert kooperativ, startet DMA und gibt den zweiten Zeichenpuffer frei.
        await leds.show(copy=False)
        pos = (pos + 1) % leds.leds
        await asyncio.sleep_ms(20)

async def main():
    leds = WS2812ParallelAsync(
        leds=200,
        first_pin=2,       # GPIO2..GPIO9
        brightness=64,
        sm_id=0,
        yield_every=8,
        reset_us=80,
    )
    asyncio.create_task(heartbeat())
    try:
        await animation(leds)
    finally:
        await leds.deinit(blackout=True)

asyncio.run(main())
