from libs.ws2812_8ch_dma import WS2812x8DMA
import time

leds = WS2812x8DMA(
    pins=(2, 3, 4, 5, 6, 7, 8, 9),
    leds=200,
    brightness=64
)

# Kanal 0 vollständig rot
leds.fill(0, (255, 0, 0))

# Kanal 1 vollständig grün
leds.fill(1, (0, 255, 0))

# Einzelne LED auf Kanal 2 blau
leds.pixel(2, 50, (0, 0, 255))

# Alle acht Puffer per DMA ausgeben
leds.show()
