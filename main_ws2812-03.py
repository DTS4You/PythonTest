import uasyncio as asyncio
from libs.ws2812_parallel_async import WS2812ParallelAsync


# 1. Schnelle Precomputed Lookup-Tabelle für HSV-Regenbogen (S=255, V=255)
def _create_rainbow_lut():
    lut = []
    for pos in range(256):
        if pos < 85:
            r, g, b = 255 - pos * 3, pos * 3, 0
        elif pos < 170:
            p = pos - 85
            r, g, b = 0, 255 - p * 3, p * 3
        else:
            p = pos - 170
            r, g, b = p * 3, 0, 255 - p * 3
        lut.append((r, g, b))
    return lut


RAINBOW_LUT = _create_rainbow_lut()


# 2. Asynchrone Animations-Schleife
async def animate_rainbow(
    driver, fps=60, speed=2, spatial_step=2, channel_phase=16
):
    """Flüssige Regenbogen-Animation über alle 8 Kanäle.

    - fps: Ziel-Bildrate (z. B. 60)
    - speed: Farbänderung pro Frame
    - spatial_step: Farbversatz von LED zu LED entlang eines Strangs
    - channel_phase: Phasenversatz zwischen den 8 Strängen
    """
    delay_ms = max(1, int(1000 / fps))
    hue_offset = 0
    num_leds = driver.leds
    lut = RAINBOW_LUT

    while True:
        # Pixel-Buffer befüllen
        for ch in range(8):
            ch_offset = hue_offset + (ch * channel_phase)
            for led in range(num_leds):
                # Schnellste Wrap-Around-Berechnung via Bit-Maskierung (& 255)
                lut_idx = (ch_offset + (led * spatial_step)) & 0xFF
                driver.pixel(ch, led, lut[lut_idx])

        # Frame senden
        # copy=False spart Zeit, da wir ohnehin im nächsten Frame alle Pixel überschreiben
        await driver.show(copy=False)

        # Farb-Offset weiterschieben
        hue_offset = (hue_offset + speed) & 0xFF

        await asyncio.sleep_ms(delay_ms)


# 3. Hauptprogramm / Event Loop
async def main():
    # Treibersystem initialisieren (200 LEDs/Strang, yield_every=32 für hohe FPS)
    matrix = WS2812ParallelAsync(
        leds=200, first_pin=2, yield_every=32, brightness=200
    )

    print("Starte Regenbogen-Animation mit 60 FPS...")

    # Animations-Task starten
    asyncio.create_task(
        animate_rainbow(
            matrix, fps=60, speed=2, spatial_step=3, channel_phase=12
        )
    )

    # Parallele Hintergrund-Aufgabe zur Demonstration der Nicht-Blockierung
    counter = 0
    while True:
        await asyncio.sleep(5)
        counter += 5
        print(
            f"[uasyncio System] Uptime: {counter}s – Animations-Task läuft flüssig weiter."
        )


# Starten
asyncio.run(main())
