import uasyncio as asyncio
from libs.ws2812_parallel_async import WS2812ParallelAsync


async def main():
    leds = WS2812ParallelAsync(
        leds=200,
        first_pin=2,
        brightness=64,
        sm_id=0,
        yield_every=8,
        reset_us=80,
    )

    try:
        leds.clear()

        leds.fill(0, (255, 0, 0))
        leds.fill(1, (0, 255, 0))
        leds.fill(2, (0, 0, 255))

        await leds.show(copy=False)
        await leds.wait()

        while True:
            await asyncio.sleep_ms(1000)

    finally:
        await leds.deinit(blackout=True)


asyncio.run(main())
