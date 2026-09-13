# ws2812_parallel_8x200_dma.py
# RP2040 / MicroPython
# 8 parallele WS2812-Kanäle an GPIO2..GPIO9
# Nur 1 PIO-State-Machine und 1 DMA-Kanal (mit Viper-Optimierung)
# Benötigt eine MicroPython-Firmware mit rp2.DMA.

from array import array
from machine import Pin
import time
import rp2

CHANNELS = 8
LEDS_PER_CHANNEL = 200
FIRST_PIN = 2            # GPIO2..GPIO9 müssen zusammenhängend sein
RESET_US = 80            # Bei manchen WS2812B-V5 / SK6812 ggf. auf 300 erhöhen


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
    # Vom Beginn eines HIGH-Pulses bis zum nächsten:
    #   HIGH alle Pins: 2 Takte
    #   Datenmaske:     5 Takte
    #   LOW:            2 Takte + 1 Takt für out(x, 8)
    # Für Maskenbit 0: HIGH 2 Takte, LOW 8 Takte
    # Für Maskenbit 1: HIGH 7 Takte, LOW 3 Takte
    wrap_target()
    out(x, 8)                       # 1 Takt, Leitungen bleiben LOW
    mov(pins, invert(null)) [1]     # alle 8 Pins HIGH, insgesamt 2 Takte
    mov(pins, x) [4]                # Bitmaske, insgesamt 5 Takte
    mov(pins, null) [1]             # alle 8 Pins LOW, 2 Takte
    wrap()


class WS2812Parallel8DMA:
    """8 gleich lange WS2812-Strips parallel über 1 SM und 1 DMA.

    API-Farbreihenfolge: RGB. Gesendet wird WS2812-typisch GRB.
    Vor show() wird aus den 8 Kanalpuffern ein Bitplane-DMA-Puffer gebaut.
    """

    def __init__(self, leds=LEDS_PER_CHANNEL, first_pin=FIRST_PIN,
                 brightness=255, sm_id=0):
        if not hasattr(rp2, "DMA"):
            raise RuntimeError("MicroPython-Firmware enthält rp2.DMA nicht")
        if leds < 1:
            raise ValueError("leds muss mindestens 1 sein")
        if not 0 <= first_pin <= 22:
            raise ValueError("Die 8 zusammenhängenden GPIOs sind ungültig")
        if not 0 <= sm_id <= 7:
            raise ValueError("sm_id muss 0..7 sein")

        self.leds = int(leds)
        self.first_pin = int(first_pin)
        self.brightness = max(0, min(255, int(brightness)))
        self.sm_id = int(sm_id)

        # Logische Farbpuffer: 8 * LEDs * 4 Byte (32-bit Integers)
        # Verwendet bytearray, um TypeError bei array-Multiplikation zu vermeiden
        self.pixels = [array("I", bytearray(self.leds * 4)) for _ in range(CHANNELS)]

        # 24 Bitplanes je LED, vier 8-Bit-Planes pro DMA-Wort (32-Bit)
        # 200 LEDs -> 4800 Bytes -> 1200 DMA-Wörter -> 4800 Byte Allokation
        self.tx = array("I", bytearray(self.leds * 24))
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
            size=2,          # Transfer-Größe: 32-Bit (0=Byte, 1=Halfword, 2=Word)
            inc_read=True,   # Pufferadresse hochzählen
            inc_write=False, # Immer in die FIFO der State Machine schreiben
            treq_sel=dreq,
        )

        self.clear(show=True)

    def _pack_grb(self, rgb):
        r, g, b = rgb
        br = self.brightness
        r = (max(0, min(255, int(r))) * br) >> 8
        g = (max(0, min(255, int(g))) * br) >> 8
        b = (max(0, min(255, int(b))) * br) >> 8
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

    @micropython.viper
    def _build_bitplanes(self):
        """Konvertiert 8 GRB-Kanäle extrem schnell in 8-Bit-Parallelmasken via Viper-Emitter.

        Jeweils vier aufeinanderfolgende Masken werden Little-Endian in ein
        32-Bit-Wort gepackt, passend zu PIO SHIFT_RIGHT und out(x, 8).
        """
        tx_ptr = ptr32(self.tx)

        # Zeiger auf die 8 Einzel-Kanäle holen für schnellen C-Speicherzugriff
        ch0 = ptr32(self.pixels[0])
        ch1 = ptr32(self.pixels[1])
        ch2 = ptr32(self.pixels[2])
        ch3 = ptr32(self.pixels[3])
        ch4 = ptr32(self.pixels[4])
        ch5 = ptr32(self.pixels[5])
        ch6 = ptr32(self.pixels[6])
        ch7 = ptr32(self.pixels[7])

        out_idx = 0
        packed_word = 0
        byte_pos = 0
        leds = int(self.leds)

        for led in range(leds):
            # Farbdaten der 8 Kanäle für das aktuelle LED-Pixel laden
            v0 = ch0[led]
            v1 = ch1[led]
            v2 = ch2[led]
            v3 = ch3[led]
            v4 = ch4[led]
            v5 = ch5[led]
            v6 = ch6[led]
            v7 = ch7[led]

            # 24 Farb-Bits (MSB bis LSB) durchlaufen
            bit = 23
            while bit >= 0:
                mask = 0
                if (v0 >> bit) & 1: mask |= 1
                if (v1 >> bit) & 1: mask |= 2
                if (v2 >> bit) & 1: mask |= 4
                if (v3 >> bit) & 1: mask |= 8
                if (v4 >> bit) & 1: mask |= 16
                if (v5 >> bit) & 1: mask |= 32
                if (v6 >> bit) & 1: mask |= 64
                if (v7 >> bit) & 1: mask |= 128

                packed_word |= (mask << (byte_pos * 8))
                byte_pos += 1

                # 4 Bytes (32 Bit) gesammelt -> in TX-Array schreiben
                if byte_pos == 4:
                    tx_ptr[out_idx] = packed_word
                    out_idx += 1
                    packed_word = 0
                    byte_pos = 0

                bit -= 1

        self._tx_valid = True

    def busy(self):
        return bool(self.dma.active())

    def wait(self):
        while self.dma.active():
            pass
        # Nach dem letzten Datenbit blockiert PIO beim nächsten OUT und
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
        first_pin=2,        # GPIO2 bis GPIO9
        brightness=64,
        sm_id=0,            # PIO0, State Machine 0
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
                for i in range(5):
                    leds.pixel(ch, pos + i, colours[ch])
                
            leds.show()
            if pos < 20:
                pos = pos + 1
            else:
                pos = 0
            time.sleep_ms(10)  # Flüssige Animation mit 10 ms Pause
    finally:
        leds.deinit()


if __name__ == "__main__":
    demo()
