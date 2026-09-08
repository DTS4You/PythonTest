import array
import time
import uasyncio as asyncio
from machine import Pin, mem32
import rp2
import uctypes


# --- 1. PIO ASSEMBLY (8-Kanal Parallel, 8 MHz) ---
@rp2.asm_pio(
    out_init=(rp2.PIO.OUT_LOW,) * 8,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    autopull=True,
    pull_thresh=32,
)
def _ws2812_8x_parallel():
    wrap_target()
    # T1: Alle 8 Pins HIGH (3 Zyklen = 375 ns)
    set(pins, 0xFF)[2]

    # T2: 8 Bits aus dem OSR an die Pins ausgeben (3 Zyklen = 375 ns)
    out(pins, 8)[2]

    # T3: Alle 8 Pins LOW (4 Zyklen = 500 ns)
    set(pins, 0x00)[3]
    wrap()


# --- 2. BIT-TRANSPOSITION (VIPER ENGINE) ---
@micropython.viper
def _transpose_8strips(framebuf_ptr: ptr8, dma_buf_ptr: ptr32, leds_per_strip: int):
    """Konvertiert 8 getrennte GRB-Buffer zeitsparend in Bit-Planes für out(pins, 8)."""
    dma_idx = 0
    for led in range(leds_per_strip):
        for bit_idx in range(24):
            bit_mask = 1 << (23 - bit_idx)
            out_byte = 0

            for strip in range(8):
                strip_offset = (strip * leds_per_strip + led) * 3

                g = int(framebuf_ptr[strip_offset])
                r = int(framebuf_ptr[strip_offset + 1])
                b = int(framebuf_ptr[strip_offset + 2])
                color24 = (g << 16) | (r << 8) | b

                if (color24 & bit_mask) != 0:
                    out_byte |= 1 << strip

            shift_pos = (3 - (dma_idx & 3)) * 8
            if (dma_idx & 3) == 0:
                dma_buf_ptr[dma_idx >> 2] = out_byte << shift_pos
            else:
                dma_buf_ptr[dma_idx >> 2] |= out_byte << shift_pos

            dma_idx += 1


# --- 3. ASYNCHRONE HAUPTKLASSE ---
class AsyncWS2812Parallel:
    """Asynchroner Treiber für 8 parallele WS2812-LED-Stränge via RP2040 PIO & DMA."""

    def __init__(self, base_pin_num: int, leds_per_strip: int, sm_id: int = 0, dma_chan: int = 0):
        self.leds_per_strip = leds_per_strip
        self.num_strips = 8
        self.dma_chan = dma_chan
        self.DMA_BASE = 0x50000000

        # 8 fortlaufende GPIO-Pins reservieren
        self.pins = [Pin(base_pin_num + i, Pin.OUT) for i in range(8)]

        # Framebuffer (GRB)
        self.framebuffer = bytearray(8 * leds_per_strip * 3)

        # Transposition-Puffer für DMA (32-Bit Worte)
        dma_words = (leds_per_strip * 24 + 3) // 4
        self.dma_buffer = array.array("I", [0] * dma_words)

        # PIO State Machine initialisieren
        self.sm = rp2.StateMachine(
            sm_id,
            _ws2812_8x_parallel,
            freq=8_000_000,
            out_base=self.pins[0],
            set_base=self.pins[0],
        )
        self.sm.active(1)

        # FIFO Zieladresse der State Machine
        pio_base = 0x50200000 if sm_id < 4 else 0x50300000
        sm_offset = (sm_id % 4) * 4
        self.dest_fifo = pio_base + 0x10 + sm_offset

        # Adress-Zeiger für Viper/DMA auflösen
        self.fb_ptr = uctypes.addressof(self.framebuffer)
        self.dma_ptr = uctypes.addressof(self.dma_buffer)

    def set_pixel(self, strip: int, led: int, r: int, g: int, b: int):
        """Setzt die Farbe einer einzelnen LED auf einem bestimmten Strang (0..7)."""
        if 0 <= strip < 8 and 0 <= led < self.leds_per_strip:
            offset = (strip * self.leds_per_strip + led) * 3
            self.framebuffer[offset] = g
            self.framebuffer[offset + 1] = r
            self.framebuffer[offset + 2] = b

    def clear(self):
        """Löscht den gesamten Framebuffer."""
        for i in range(len(self.framebuffer)):
            self.framebuffer[i] = 0

    def is_busy(self) -> bool:
        """Prüft, ob der DMA-Kanal noch Daten an die PIO überträgt."""
        base = self.DMA_BASE + (self.dma_chan * 0x40)
        return bool(mem32[base + 0x0C] & (1 << 24))

    async def show(self):
        """Transponiert die Daten asynchron und startet die DMA-Übertragung."""
        # 1. Warten, falls die vorherige Übertragung noch läuft
        while self.is_busy():
            await asyncio.sleep_ms(1)

        # 2. Transposition der Bit-Planes (gibt der Eventloop kurz Rechenzeit)
        _transpose_8strips(self.fb_ptr, self.dma_ptr, self.leds_per_strip)
        await asyncio.sleep_ms(0)

        # 3. Latch / Reset-Zeit der WS2812 einhalten (> 280 µs)
        time.sleep_us(300)

        # 4. DMA konfigurieren und feuern
        base = self.DMA_BASE + (self.dma_chan * 0x40)
        mem32[base + 0x00] = self.dma_ptr
        mem32[base + 0x04] = self.dest_fifo
        mem32[base + 0x08] = len(self.dma_buffer)

        # CTRL/TRIGGER: DREQ PIO0_TX0, INCR_READ, 32-Bit, ENABLE
        dreq = 0 if self.sm.exec else 0  # Default PIO0 DREQ
        mem32[base + 0x0C] = (dreq << 15) | (1 << 4) | (2 << 2) | 1

    def cleanup(self):
        """Stoppt die DMA und deaktiviert die State Machine."""
        base = self.DMA_BASE + (self.dma_chan * 0x40)
        mem32[base + 0x0C] = 0
        self.sm.active(0)

