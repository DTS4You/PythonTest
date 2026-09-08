import uasyncio as asyncio
import math
from libs.modul_ws2812_v2 import AsyncWS2812Parallel

# Konfiguration
BASE_PIN = 2          # Verwendet GP2, GP3, GP4, GP5, GP6, GP7, GP8, GP9
LEDS_PER_STRIP = 200  # 200 LEDs pro Strang (Insgesamt 1.600 LEDs)


async def animate_rainbow(leds: AsyncWS2812Parallel):
    """Animationstask: Berechnet eine wandernde Regenbogenwelle für alle 8 Stränge."""
    step = 0
    while True:
        for strip in range(8):
            for led in range(leds.leds_per_strip):
                # Regenbogen-Farbverlauf berechnen
                hue = (led * 10 + step + (strip * 20)) % 255
                
                # Einfache HSV zu RGB Konvertierung
                if hue < 85:
                    r, g, b = 85 - hue, hue, 0
                elif hue < 170:
                    hue -= 85
                    r, g, b = 0, 85 - hue, hue
                else:
                    hue -= 170
                    r, g, b = hue, 0, 85 - hue
                
                # Helligkeit dimmen
                leds.set_pixel(strip, led, r // 4, g // 4, b // 4)

        # Daten asynchron an die LEDs senden
        await leds.show()
        
        step = (step + 4) % 255
        await asyncio.sleep_ms(10)  # ~30-40 FPS Kontroll-Rate


async def heartbeat_task():
    """Ein paralleler Task, der zeigt, dass die Eventloop nicht blockiert wird."""
    counter = 0
    while True:
        counter += 1
        print(f"[Async Status] Event-Loop läuft flüssig... Tick: {counter}")
        await asyncio.sleep(2)


async def main():
    print("Initialisiere 8x WS2812 Parallel-Treiber...")
    leds = AsyncWS2812Parallel(base_pin_num=BASE_PIN, leds_per_strip=LEDS_PER_STRIP)

    try:
        # Starte beide Tasks parallel
        await asyncio.gather(
            animate_rainbow(leds),
            heartbeat_task()
        )
    finally:
        leds.cleanup()
        print("Treiber gestoppt und Ressourcen freigegeben.")


if __name__ == "__main__":
    asyncio.run(main())

