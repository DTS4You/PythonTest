# ws2812_parallel_8x200_direct_db.py
# RP2040 / MicroPython
# High-Performance WS2812 Driver (Direct Bitplane Drawing + Double Buffering)

from array import array
from machine import Pin
import time
import rp2
import machine

# Hardware-Takt auf 250 MHz anheben für maximale Berechnungsgeschwindigkeit
machine.freq(250_000_000)

CHANNELS = 8
LEDS_PER_CHANNEL = 200
FIRST_PIN = 2            # GPIO2..GPIO9
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
    wrap_target()
    out(x, 8)                       # 1 Takt, Leitungen LOW
    mov(pins, invert(null)) [1]     # alle 8 Pins HIGH (2 Takte)
    mov(pins, x) [4]                # Bitmaske (5 Takte)
    mov(pins, null) [1]             # alle 8 Pins LOW (2 Takte)
    wrap()


class WS2812DirectDMA:
    """8-Kanal Parallel-Triebwerk ohne Konvertierungslatenz.
    
    Nutzt Direct Bitplane Writing und Double-Buffering.
    """

    def __init__(self, leds=LEDS_PER_CHANNEL, first_pin=FIRST_PIN,
                 brightness=255, sm_id=0):
        if not hasattr(rp2, "DMA"):
            raise RuntimeError("MicroPython-Firmware enthält rp2.DMA nicht")
        
        self.leds = int(leds)
        self.first_pin = int(first_pin)
        self.brightness = max(0, min(255, int(brightness)))
        self.sm_id = int(sm_id)
        
        # Puffergröße: 24 Bitplanes je LED, 4 Bytes pro DMA-Wort (32-Bit)
        self.words_per_buffer = self.leds * 6
        
        # Double-Buffering Arrays (Front- & Backbuffer)
        self.tx_buf0 = array("I", bytearray(self.words_per_buffer * 4))
        self.tx_buf1 = array("I", bytearray(self.words_per_buffer * 4))
        
        # Puffer-Indizes (0 = buf0 schreibt, buf1 sendet / 1 = vice versa)
        self.active_write = 0
        
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
            size=2,          # 32-Bit Wörter
            inc_read=True,
            inc_write=False,
            treq_sel=dreq,
        )

        self.clear(show=True)

    @micropython.viper
    def _set_pixel_fast(self, buf: object, channel: int, index: int, grb: int):
        """Schreibt Farb-Bits direkt in die DMA Bitplanes des Zielpuffers."""
        buf_ptr = ptr32(buf)
        base_word = index * 6
        ch_mask = 1 << channel

        for bit in range(23, -1, -1):
            bit_idx = 23 - bit
            word_offset = bit_idx >> 2        # bit_idx // 4
            byte_pos = bit_idx & 3            # bit_idx % 4
            shift = byte_pos << 3             # byte_pos * 8

            target_word_idx = base_word + word_offset
            current_val = buf_ptr[target_word_idx]

            if (grb >> bit) & 1:
                current_val |= (ch_mask << shift)
            else:
                current_val &= ~(ch_mask << shift)

            buf_ptr[target_word_idx] = current_val

    def _pack_grb(self, rgb):
        r, g, b = rgb
        br = self.brightness
        r = (max(0, min(255, int(r))) * br) >> 8
        g = (max(0, min(255, int(g))) * br) >> 8
        b = (max(0, min(255, int(b))) * br) >> 8
        return (g << 16) | (r << 8) | b

    def pixel(self, channel, index, rgb):
        if not 0 <= channel < CHANNELS:
            raise IndexError("channel muss 0..7 sein")
        if not 0 <= index < self.leds:
            raise IndexError("LED-Index ausserhalb des Puffers")
            
        grb = self._pack_grb(rgb)
        buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
        self._set_pixel_fast(buf, channel, index, grb)

    def fill(self, channel, rgb):
        if not 0 <= channel < CHANNELS:
            raise IndexError("channel muss 0..7 sein")
        
        grb = self._pack_grb(rgb)
        buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
        for i in range(self.leds):
            self._set_pixel_fast(buf, channel, i, grb)

    def fill_all(self, rgb):
        grb = self._pack_grb(rgb)
        buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
        for ch in range(CHANNELS):
            for i in range(self.leds):
                self._set_pixel_fast(buf, ch, i, grb)

    def clear(self, show=False):
        buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
        for i in range(len(buf)):
            buf[i] = 0
            
        if show:
            self.show()

    def busy(self):
        return bool(self.dma.active())

    def wait(self):
        while self.dma.active():
            pass
        time.sleep_us(RESET_US)

    def show(self, wait=False):
        self.wait()

        read_buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
        write_buf = self.tx_buf1 if self.active_write == 0 else self.tx_buf0

        self.dma.config(
            read=read_buf,
            write=self.sm,
            count=len(read_buf),
            ctrl=self.dma_ctrl,
            trigger=True,
        )

        write_buf[:] = read_buf[:]
        self.active_write = 1 if self.active_write == 0 else 0

        if wait:
            self.wait()

    def deinit(self):
        self.wait()
        self.clear(show=True)
        self.sm.active(0)
        self.dma.close()


def demo():
    leds = WS2812DirectDMA(
        leds=200,
        first_pin=2,
        brightness=64,
        sm_id=0,
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
                for _ in range(20):
                    for i in range(5):
                        leds.pixel(ch, pos + i, colours[ch])
            
            leds.show(wait=False)
            if pos < 19:
                pos = pos + 1
            else:
                pos = 0
            time.sleep_ms(10)

    finally:
        leds.deinit()


if __name__ == "__main__":
    demo()
