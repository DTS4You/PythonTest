# ws2812_parallel_8x200_dma.py
# RP2040 / MicroPython
# 8 parallele WS2812-Kanaele an GPIO2..GPIO9
# Nur 1 PIO-State-Machine und 1 DMA-Kanal
# Benoetigt eine MicroPython-Firmware mit rp2.DMA.

from array import array
from machine import Pin
import time
import rp2

CHANNELS = 8
LEDS_PER_CHANNEL = 200
FIRST_PIN = 2              # GPIO2..GPIO9 muessen zusammenhaengend sein
RESET_US = 80


@rp2.asm_pio(
    out_init=(
        rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,
    ),
    out_shiftdir=rp2.PIO.SHIFT_RIGHT,
    autopull=True,
    pull_thresh=32,
    fifo_join=rp2.PIO.JOIN_TX,
)
def ws2812_parallel8():
    # Ein Byte im OSR ist eine Bitplane:
    # Bit 0 -> GPIO2/Kanal0 ... Bit 7 -> GPIO9/Kanal7.
    # 10 Takte bei 8 MHz ergeben 1,25 us pro WS2812-Bit.
    #
    # Vom Beginn eines HIGH-Pulses bis zum naechsten:
    #   HIGH alle Pins: 2 Takte
    #   Datenmaske:     5 Takte
    #   LOW:            2 Takte + 1 Takt fuer out(x, 8)
    # Fuer Maskenbit 0: HIGH 2 Takte, LOW 8 Takte
    # Fuer Maskenbit 1: HIGH 7 Takte, LOW 3 Takte
    wrap_target()
    out(x, 8)                      # 1 Takt, Leitungen bleiben LOW
    mov(pins, invert(null)) [1]    # alle 8 Pins HIGH, insgesamt 2 Takte
    mov(pins, x) [4]               # Bitmaske, insgesamt 5 Takte
    mov(pins, null) [1]            # alle 8 Pins LOW, 2 Takte
    wrap()


class WS2812Parallel8DMA:
    """8 gleich lange WS2812-Strips parallel ueber 1 SM und 1 DMA.

    API-Farbreihenfolge: RGB. Gesendet wird WS2812-typisch GRB.
    Vor show() wird aus den 8 Kanalpuffern ein Bitplane-DMA-Puffer gebaut.
    """

    def __init__(self, leds=LEDS_PER_CHANNEL, first_pin=FIRST_PIN,
                 brightness=255, sm_id=0):
        if not hasattr(rp2, "DMA"):
            raise RuntimeError("MicroPython-Firmware enthaelt rp2.DMA nicht")
        if leds < 1:
            raise ValueError("leds muss mindestens 1 sein")
        if not 0 <= first_pin <= 22:
            raise ValueError("Die 8 zusammenhaengenden GPIOs sind ungueltig")
        if not 0 <= sm_id <= 7:
            raise ValueError("sm_id muss 0..7 sein")

        self.leds = int(leds)
        self.first_pin = int(first_pin)
        self.brightness = max(0, min(255, int(brightness)))
        self.sm_id = int(sm_id)

        # Logische Farbpuffer: 8 * LEDs * 4 Byte.
        self.pixels = [array("I", [0]) * self.leds for _ in range(CHANNELS)]

        # 24 Bitplanes je LED, vier 8-Bit-Planes pro DMA-Wort.
        # 200 LEDs -> 4800 Bytes -> 1200 DMA-Woerter.
        self.tx = array("I", [0]) * (self.leds * 6)
        self._tx_valid = False

        self.sm = rp2.StateMachine(
            self.sm_id,
            ws2812_parallel8,
            freq=8_000_000,
            out_base=Pin(self.first_pin),
        )
        self.sm.active(1)

        self.dma = rp2.DMA()
        pio_num = self.sm_id >> 2
        local_sm = self.sm_id & 3
        dreq = (pio_num << 3) + local_sm
        self.dma_ctrl = self.dma.pack_ctrl(
            size=2,
            inc_read=True,
            inc_write=False,
            treq_sel=dreq,
        )

        self.clear(show=True)

    def _pack_grb(self, rgb):
        r, g, b = rgb
        br = self.brightness
        r = (max(0, min(255, int(r))) * br) // 255
        g = (max(0, min(255, int(g))) * br) // 255
        b = (max(0, min(255, int(b))) * br) // 255
        return (g << 16) | (r << 8) | b

    def pixel(self, channel, index, rgb=None):
        if not 0 <= channel < CHANNELS:
            raise IndexError("channel muss 0..7 sein")
        if not 0 <= index < self.leds:
            raise IndexError("LED-Index ausserhalb des Puffers")
        if rgb is None:
            value = self.pixels[channel][index]
            return ((value >> 8) & 0xff, (value >> 16) & 0xff, value & 0xff)
        self.pixels[channel][index] = self._pack_grb(rgb)
        self._tx_valid = False

    def fill(self, channel, rgb):
        if not 0 <= channel < CHANNELS:
            raise IndexError("channel muss 0..7 sein")
        value = self._pack_grb(rgb)
        dst = self.pixels[channel]
        for i in range(self.leds):
            dst[i] = value
        self._tx_valid = False

    def fill_all(self, rgb):
        value = self._pack_grb(rgb)
        for ch in range(CHANNELS):
            dst = self.pixels[ch]
            for i in range(self.leds):
                dst[i] = value
        self._tx_valid = False

    def clear(self, show=False):
        for ch in range(CHANNELS):
            dst = self.pixels[ch]
            for i in range(self.leds):
                dst[i] = 0
        self._tx_valid = False
        if show:
            self.show()

    def _build_bitplanes(self):
        """Konvertiert 8 GRB-Kanaele in 8-Bit-Parallelmasken.

        Je vier aufeinanderfolgende Masken werden little-endian in ein
        32-Bit-Wort gepackt, passend zu PIO SHIFT_RIGHT und out(x, 8).
        """
        tx = self.tx
        out_index = 0
        packed_word = 0
        byte_pos = 0

        for led in range(self.leds):
            for bit in range(23, -1, -1):
                mask = 0
                bit_value = 1 << bit
                for ch in range(CHANNELS):
                    if self.pixels[ch][led] & bit_value:
                        mask |= 1 << ch

                packed_word |= mask << (byte_pos * 8)
                byte_pos += 1
                if byte_pos == 4:
                    tx[out_index] = packed_word
                    out_index += 1
                    packed_word = 0
                    byte_pos = 0

        self._tx_valid = True

    def busy(self):
        return bool(self.dma.active())

    def wait(self):
        while self.dma.active():
            pass
        # Nach dem letzten Datenbit blockiert PIO beim naechsten OUT und
        # die Leitungen bleiben LOW. Diese Pause erzeugt den WS2812-Latch.
        time.sleep_us(RESET_US)

    def show(self, wait=True):
        # Nie den Puffer umbauen, solange DMA daraus liest.
        self.wait()
        if not self._tx_valid:
            self._build_bitplanes()

        self.dma.config(
            read=self.tx,
            write=self.sm,
            count=len(self.tx),
            ctrl=self.dma_ctrl,
            trigger=True,
        )
        if wait:
            self.wait()

    def deinit(self):
        self.wait()
        self.clear(show=True)
        self.sm.active(0)
        self.dma.close()


# Test: je Kanal ein andersfarbiger, phasenverschobener Laufpunkt.
def demo():
    leds = WS2812Parallel8DMA(
        leds=200,
        first_pin=2,       # GPIO2 bis GPIO9
        brightness=64,
        sm_id=0,           # PIO0, State Machine 0
    )
    colours = (
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (0, 255, 255), (255, 0, 255), (255, 128, 0), (255, 255, 255),
    )

    try:
        pos = 0
        while True:
            leds.clear()
            for ch in range(CHANNELS):
                leds.pixel(ch, (pos + ch * 11) % leds.leds, colours[ch])
            leds.show()
            pos = (pos + 1) % leds.leds
            time.sleep_ms(20)
    finally:
        leds.deinit()


if __name__ == "__main__":
    demo()
