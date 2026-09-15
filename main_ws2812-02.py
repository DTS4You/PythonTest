#==============================================================================
# Lauffähige Version 1.00
# libs.ws2812_parallel
#==============================================================================
import asyncio
from libs.ws2812_parallel_v1 import WS2812DirectDMA

COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (0, 255, 255), (255, 0, 255), (255, 128, 0), (255, 255, 255),
]

async def animate_leds(leds):
    pos = 0
    while True:
        leds.clear()
        for ch in range(8):
            for i in range(5):
                leds.pixel(ch, (pos + i) % leds.leds, COLORS[ch])

        leds.show(wait=False)
        if pos < 19:
            pos = pos + 1
        else:
            pos = 0
        await asyncio.sleep_ms(30)

async def main():
    leds = WS2812DirectDMA(leds=200, first_pin=2, brightness=64)
    try:
        await animate_leds(leds)
    finally:
        leds.deinit()

asyncio.run(main())
