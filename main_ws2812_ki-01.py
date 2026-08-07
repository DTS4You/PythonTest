# ws2812_8way_dma.py
#
# RP2040 / Raspberry Pi Pico
# MicroPython
#
# 8 parallele WS2812-Ausgänge über:
# - 1 PIO-State-Machine
# - 1 DMA-Kanal
# - 8 GPIOs als paralleler Datenbus
# - Double-Buffering
#
# GPIO first_pin + 0 -> Stripe 0
# GPIO first_pin + 1 -> Stripe 1
# ...
# GPIO first_pin + 7 -> Stripe 7

import array
import machine
import rp2
import uctypes
import utime
import gc
from micropython import const


# =============================================================================
# PIO-Programm: 8 parallele WS2812-Ausgänge
# =============================================================================
#
# Für jedes WS2812-Bit wird ein 8-Bit-Maskenwert verarbeitet:
#
#   Bit 0 im Byte -> Ausgang 0
#   Bit 1 im Byte -> Ausgang 1
#   ...
#   Bit 7 im Byte -> Ausgang 7
#
# Ablauf pro WS2812-Bit:
#
#   1. alle 8 Pins HIGH
#   2. out(pins, 8) gibt die Maske aus
#      - Stripe-Bit = 1 bleibt HIGH
#      - Stripe-Bit = 0 geht LOW
#   3. alle Pins LOW
#
# Damit entsteht:
#   0-Bit: kurz HIGH, dann LOW
#   1-Bit: länger HIGH, dann LOW

@rp2.asm_pio(
    out_shiftdir=rp2.PIO.SHIFT_RIGHT,
    autopull=True,
    pull_thresh=32,
    out_init=(
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
    )
)
def ws2812_8way_pio():
    # 8 MHz PIO Clock
    # 10 Takte pro Bit = 1,25 us
    #
    # Annäherung:
    # HIGH-Start für alle Kanäle
    # nach kurzer Zeit Maske ausgeben
    # danach alles LOW

    wrap_target()

    # Alle 8 Ausgänge HIGH
    mov(pins, invert(null)) [2]

    # Maske aus OSR auf 8 Pins ausgeben
    # 0-Kanäle werden LOW
    # 1-Kanäle bleiben HIGH
    out(pins, 8) [4]

    # Alle 8 Ausgänge LOW
    mov(pins, null) [2]

    wrap()


# =============================================================================
# DMA Register
# =============================================================================

DMA_BASE              = const(0x50000000)
DMA_CH_SIZE           = const(0x40)

DMA_READ_ADDR         = const(0x00)
DMA_WRITE_ADDR        = const(0x04)
DMA_TRANS_COUNT       = const(0x08)
DMA_CTRL_TRIG         = const(0x0C)

DMA_CTRL_EN           = const(1 << 0)
DMA_CTRL_DATA_32      = const(2 << 2)
DMA_CTRL_INCR_READ    = const(1 << 4)
DMA_CTRL_INCR_WRITE   = const(1 << 5)
DMA_CTRL_TREQ_SHIFT   = const(15)

PIO0_BASE             = const(0x50200000)
PIO1_BASE             = const(0x50300000)
PIO_TXF_OFFSET        = const(0x10)

PIO0_DREQ_TX_BASE     = const(0)
PIO1_DREQ_TX_BASE     = const(8)


class DMAChannel:
    def __init__(self, channel):
        self.channel = channel
        self.base = DMA_BASE + channel * DMA_CH_SIZE

    def active(self):
        return (machine.mem32[self.base + DMA_CTRL_TRIG] >> 24) & 1

    def abort(self):
        machine.mem32[self.base + DMA_CTRL_TRIG] = 0

    def start(self, read_addr, write_addr, count_words, treq_sel):
        ctrl = (
            DMA_CTRL_EN |
            DMA_CTRL_DATA_32 |
            DMA_CTRL_INCR_READ |
            (treq_sel << DMA_CTRL_TREQ_SHIFT)
        )

        machine.mem32[self.base + DMA_READ_ADDR] = read_addr
        machine.mem32[self.base + DMA_WRITE_ADDR] = write_addr
        machine.mem32[self.base + DMA_TRANS_COUNT] = count_words
        machine.mem32[self.base + DMA_CTRL_TRIG] = ctrl


# =============================================================================
# 8-Way WS2812 Treiber
# =============================================================================

class WS2812_8WAY_DMA:
    def __init__(
        self,
        first_pin,
        leds_per_strip,
        sm_id=0,
        dma_channel=0,
        brightness=1.0,
        reset_us=80
    ):
        self.first_pin = first_pin
        self.leds_per_strip = leds_per_strip
        self.channels = 8
        self.sm_id = sm_id
        self.reset_us = reset_us

        if brightness < 0:
            brightness = 0
        if brightness > 1:
            brightness = 1
        self.brightness = brightness

        # Pro LED: 24 WS2812-Bits.
        # Pro Bit: 8 parallele Kanäle als ein Byte.
        # Die PIO zieht 32 Bit pro Pull, also 4 Bitplanes pro Word.
        self.bitplane_bytes = leds_per_strip * 24
        self.word_count = (self.bitplane_bytes + 3) // 4

        self.buf_a = array.array("I", [0] * self.word_count)
        self.buf_b = array.array("I", [0] * self.word_count)

        self.draw_buf = self.buf_a
        self.send_buf = self.buf_b

        self.dma = DMAChannel(dma_channel)

        # MicroPython StateMachine IDs:
        # 0..3 liegen normalerweise auf PIO0,
        # 4..7 liegen normalerweise auf PIO1.
        if sm_id < 4:
            self.pio_base = PIO0_BASE
            self.pio_sm = sm_id
            self.pio_dreq = PIO0_DREQ_TX_BASE + sm_id
        else:
            self.pio_base = PIO1_BASE
            self.pio_sm = sm_id - 4
            self.pio_dreq = PIO1_DREQ_TX_BASE + self.pio_sm

        self.pio_txf_addr = self.pio_base + PIO_TXF_OFFSET + 4 * self.pio_sm

        # Acht Pins ab first_pin als OUT-Pin-Gruppe.
        self.sm = rp2.StateMachine(
            sm_id,
            ws2812_8way_pio,
            freq=8_000_000,
            out_base=machine.Pin(first_pin)
        )
        self.sm.active(1)

        self._active_transfer = False
        self._last_done_us = utime.ticks_us()

        self.clear()
        gc.collect()

    # -------------------------------------------------------------------------
    # Interne Hilfsfunktionen
    # -------------------------------------------------------------------------

    def _scale(self, value):
        value = int(value * self.brightness)
        if value < 0:
            return 0
        if value > 255:
            return 255
        return value

    def _pack_grb24(self, r, g, b):
        r = self._scale(r)
        g = self._scale(g)
        b = self._scale(b)

        # WS2812 erwartet GRB, MSB zuerst.
        return (g << 16) | (r << 8) | b

    def _set_bitplane_bit(self, bitplane_index, lane, value):
        word_index = bitplane_index >> 2
        byte_shift = (bitplane_index & 3) * 8

        lane_mask = 1 << lane
        byte_mask = 0xFF << byte_shift

        old_word = self.draw_buf[word_index]
        old_byte = (old_word >> byte_shift) & 0xFF

        if value:
            new_byte = old_byte | lane_mask
        else:
            new_byte = old_byte & ~lane_mask

        self.draw_buf[word_index] = (old_word & ~byte_mask) | (new_byte << byte_shift)

    # -------------------------------------------------------------------------
    # Pixel API
    # -------------------------------------------------------------------------

    def set_rgb(self, lane, index, r, g, b):
        """
        lane:
            0..7, also der Ausgang / Stripe

        index:
            LED-Index auf diesem Stripe

        Farbe:
            r, g, b je 0..255
        """

        if lane < 0 or lane > 7:
            raise ValueError("lane muss 0..7 sein")

        if index < 0 or index >= self.leds_per_strip:
            raise ValueError("index außerhalb des LED-Bereichs")

        color = self._pack_grb24(r, g, b)

        base = index * 24

        for bit in range(24):
            bit_is_set = (color & (1 << (23 - bit))) != 0
            self._set_bitplane_bit(base + bit, lane, bit_is_set)

    def fill_lane(self, lane, r, g, b):
        for i in range(self.leds_per_strip):
            self.set_rgb(lane, i, r, g, b)

    def fill_all(self, r, g, b):
        for lane in range(8):
            self.fill_lane(lane, r, g, b)

    def clear(self):
        for i in range(self.word_count):
            self.draw_buf[i] = 0

    def set_brightness(self, brightness):
        if brightness < 0:
            brightness = 0
        if brightness > 1:
            brightness = 1
        self.brightness = brightness

    # -------------------------------------------------------------------------
    # DMA / Ausgabe
    # -------------------------------------------------------------------------

    def ready(self):
        if self._active_transfer and not self.dma.active():
            self._active_transfer = False
            self._last_done_us = utime.ticks_us()

        if self.dma.active():
            return False

        elapsed = utime.ticks_diff(utime.ticks_us(), self._last_done_us)
        return elapsed >= self.reset_us

    def wait(self):
        while not self.ready():
            pass

    def show_async(self):
        """
        Nicht blockierend.
        Gibt True zurück, wenn ein neuer DMA-Transfer gestartet wurde.
        Gibt False zurück, wenn der vorige Transfer oder die Reset-Pause noch läuft.
        """

        if not self.ready():
            return False

        # Double-Buffering:
        # Gezeichneter Buffer wird gesendet.
        self.draw_buf, self.send_buf = self.send_buf, self.draw_buf

        self.dma.abort()

        self.dma.start(
            read_addr=uctypes.addressof(self.send_buf),
            write_addr=self.pio_txf_addr,
            count_words=self.word_count,
            treq_sel=self.pio_dreq
        )

        self._active_transfer = True
        return True

    def show(self):
        while not self.show_async():
            pass
        self.wait()

    # -------------------------------------------------------------------------
    # Demo-Helfer
    # -------------------------------------------------------------------------

    def wheel(self, pos):
        pos = pos & 255
        if pos < 85:
            return 255 - pos * 3, pos * 3, 0
        if pos < 170:
            pos -= 85
            return 0, 255 - pos * 3, pos * 3
        pos -= 170
        return pos * 3, 0, 255 - pos * 3


# =============================================================================
# Beispiel
# =============================================================================

if __name__ == "__main__":
    leds = WS2812_8WAY_DMA(
        first_pin=0,          # GPIO0..GPIO7
        leds_per_strip=150,   # 150 LEDs pro Ausgang
        sm_id=0,
        dma_channel=0,
        brightness=0.25
    )

    leds.fill_all(0, 0, 0)
    leds.show()

    offset = 0

    while True:
        # Nächsten Frame in draw_buf vorbereiten,
        # während der vorige Frame ggf. noch per DMA läuft.

        leds.clear()

        for lane in range(8):
            for i in range(leds.leds_per_strip):
                r, g, b = leds.wheel((i * 256 // leds.leds_per_strip) + offset + lane * 20)
                leds.set_rgb(lane, i, r, g, b)

        if leds.show_async():
            offset = (offset + 2) & 255

        utime.sleep_ms(1)

