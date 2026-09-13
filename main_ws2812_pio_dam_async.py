import uasyncio as asyncio
from libs.ws2812_parallel_async import WS2812ParallelAsync


async def main():
    leds = WS2812ParallelAsync(
        leds=20,
        first_pin=2,
        brightness=64,
        sm_id=0,
        yield_every=8,
        reset_us=80,
    )


    while(True):
        leds.clear()

        for s in range(8):
            for i in range(20):
                leds.pixel(s,i,(0,50,0))
        
        await leds.show(copy=False)

        asyncio.sleep_ms(20)

        leds.clear()

        await leds.show(copy=False)
    
        asyncio.sleep_ms(20)


asyncio.run(main())
