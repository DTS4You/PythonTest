# ws2812_8ch_dma.py
# RP2040 / MicroPython: 8 unabhaengige WS2812-Kanaele mit PIO + DMA
# Je Kanal standardmaessig 200 LEDs.
# Benoetigt eine MicroPython-Firmware mit rp2.DMA.

from array import array
from machine import Pin
import time
import rp2

CHANNELS = 8
LEDS_PER_CHANNEL = 200
DEFAULT_PINS = (2, 3, 4, 5, 6, 7, 8, 9)
RESET_US = 80


@rp2.asm_pio(
    sideset_init=rp2.PIO.OUT_LOW,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    autopull=True,
    pull_thresh=24,
    fifo_join=rp2.PIO.JOIN_TX,
)
def _ws2812():
    # 10 PIO-Takte pro Bit bei 8 MHz = 1,25 us pro Bit.
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0) [T3 - 1]
    jmp(not_x, "do_zero")  .side(1) [T1 - 1]
    jmp("bitloop")         .side(1) [T2 - 1]
    label("do_zero")
    nop()                   .side(0) [T2 - 1]
    wrap()


class WS2812x8DMA:
    """Acht WS2812-Strips, je Strip eine PIO-SM und ein DMA-Kanal.

    Farbreihenfolge der API: RGB. Auf dem Draht wird WS2812-typisch GRB gesendet.
    Die Frame-Puffer enthalten bereits linksbuendig ausgerichtete 24-Bit-Werte,
    damit DMA die Woerter ohne CPU-Nachbearbeitung direkt in die PIO-FIFOs schreibt.
    """

    def __init__(self, pins=DEFAULT_PINS, leds=LEDS_PER_CHANNEL, brightness=255):
        if not hasattr(rp2, "DMA"):
            raise RuntimeError("Diese MicroPython-Firmware enthaelt rp2.DMA nicht")
        if len(pins) != CHANNELS:
            raise ValueError("Es werden genau 8 GPIO-Pins benoetigt")
        if leds < 1:
            raise ValueError("leds muss groesser als 0 sein")

        self.leds = leds
        self.brightness = max(0, min(255, int(brightness)))
        self.sms = []
        self.dmas = []
        self.ctrl = []
        self.buf = [array("I", [0]) * leds for _ in range(CHANNELS)]

        for ch, gpio in enumerate(pins):
            sm = rp2.StateMachine(
                ch,
                _ws2812,
                freq=8_000_000,
                sideset_base=Pin(gpio, Pin.OUT),
            )
            sm.active(1)

            dma = rp2.DMA()
            pio_num = 0 if ch < 4 else 1
            local_sm = ch & 3
            dreq = (pio_num << 3) + local_sm
            ctrl = dma.pack_ctrl(
                size=2,          # 32-Bit-Transfer
                inc_read=True,
                inc_write=False,
                treq_sel=dreq,   # pacing durch TX-FIFO der jeweiligen SM
            )

            self.sms.append(sm)
            self.dmas.append(dma)
            self.ctrl.append(ctrl)

        self.clear(show=True)

    @staticmethod
    def _pack_grb(r, g, b, brightness):
        r = (max(0, min(255, int(r))) * brightness) // 255
        g = (max(0, min(255, int(g))) * brightness) // 255
        b = (max(0, min(255, int(b))) * brightness) // 255
        # PIO SHIFT_LEFT zieht die obersten 24 Bits; daher << 8.
        return ((g << 16) | (r << 8) | b) << 8

    def pixel(self, channel, index, rgb):
        r, g, b = rgb
        self.buf[channel][index] = self._pack_grb(r, g, b, self.brightness)

    def fill(self, channel, rgb):
        value = self._pack_grb(rgb[0], rgb[1], rgb[2], self.brightness)
        a = self.buf[channel]
        for i in range(self.leds):
            a[i] = value

    def fill_all(self, rgb):
        for ch in range(CHANNELS):
            self.fill(ch, rgb)

    def clear(self, show=False):
        for ch in range(CHANNELS):
            a = self.buf[ch]
            for i in range(self.leds):
                a[i] = 0
        if show:
            self.show()

    def busy(self):
        return any(d.active() for d in self.dmas)

    def wait(self):
        while self.busy():
            pass
        # WS2812-Latch/Reset: alle Datenleitungen bleiben durch PIO LOW.
        time.sleep_us(RESET_US)

    def show(self, wait=True):
        # Vorherigen Frame abschliessen, damit Puffer nicht waehrend DMA geaendert werden.
        self.wait()

        # Alle 8 DMA-Kanaele zuerst konfigurieren, danach nahezu gleichzeitig starten.
        for ch in range(CHANNELS):
            self.dmas[ch].config(
                read=self.buf[ch],
                write=self.sms[ch],
                count=self.leds,
                ctrl=self.ctrl[ch],
                trigger=False,
            )
        for dma in self.dmas:
            dma.active(1)

        if wait:
            self.wait()

    def deinit(self):
        self.wait()
        self.clear(show=True)
        for sm in self.sms:
            sm.active(0)
        for dma in self.dmas:
            dma.close()


# Demonstration: wandernder Punkt, auf jedem Kanal phasenverschoben.
def demo():
    strips = WS2812x8DMA(
        pins=(0, 1, 2, 3, 4, 5, 6, 7),
        leds=200,
        brightness=64,
    )
    colours = (
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (0, 255, 255), (255, 0, 255), (255, 128, 0), (255, 255, 255),
    )
    try:
        pos = 0
        while True:
            strips.clear(show=False)
            for ch in range(CHANNELS):
                strips.pixel(ch, (pos + ch * 7) % strips.leds, colours[ch])
            strips.show()
            pos = (pos + 1) % strips.leds
            time.sleep_ms(20)
    finally:
        strips.deinit()


if __name__ == "__main__":
    demo()
