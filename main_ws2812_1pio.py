from libs.ws2812_1pio_dma import WS2812Parallel8DMA
import time

leds = WS2812Parallel8DMA(
    leds=200,
    first_pin=2,
    brightness=64,
    sm_id=0
)

# Kanal 0 vollständig rot
leds.fill(0, (255, 0, 0))

# Kanal 1 vollständig grün
leds.fill(1, (0, 255, 0))

# Einzelne blaue LED auf Kanal 2
leds.pixel(2, 50, (0, 0, 255))

# Alle acht Kanäle parallel ausgeben
leds.show()

while True:
    time.sleep(1)

