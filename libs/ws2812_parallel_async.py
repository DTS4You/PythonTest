# ws2812_parallel_async.py
# RP2040 MicroPython: 8 x WS2812 parallel, GPIO2..GPIO9
# 1 PIO-State-Machine, 1 DMA-Kanal, Double Buffering, uasyncio

from array import array
from machine import Pin
import rp2
import uasyncio as asyncio

CHANNELS = 8


@rp2.asm_pio(
    out_init=(rp2.PIO.OUT_LOW,) * 8,
    out_shiftdir=rp2.PIO.SHIFT_RIGHT,
    autopull=True,
    pull_thresh=32,
    fifo_join=rp2.PIO.JOIN_TX,
)
def ws2812_parallel8():
    # 10 Takte/Bit bei 8 MHz = 1,25 us.
    # 0-Bit: HIGH 2, LOW 8 Takte. 1-Bit: HIGH 7, LOW 3 Takte.
    wrap_target()
    out(x, 8)
    mov(pins, invert(null)) [1]
    mov(pins, x) [4]
    mov(pins, null) [1]
    wrap()


class WS2812ParallelAsync:
    """8 parallele WS2812-Strips mit zwei Zeichen- und zwei DMA-Puffern.

    draw buffer: wird von pixel()/fill()/clear() beschrieben.
    queued buffer: wird in Bitplanes konvertiert und per DMA gesendet.
    Nach erfolgreichem show() werden die Zeichenpuffer vertauscht. Damit kann
    die Anwendung den naechsten Frame zeichnen, waehrend DMA den aktuellen sendet.
    """

    def __init__(self, leds=200, first_pin=2, brightness=255, sm_id=0,
                 yield_every=8, reset_us=80):
        if not hasattr(rp2, "DMA"):
            raise RuntimeError("Diese Firmware enthaelt rp2.DMA nicht")
        if leds < 1:
            raise ValueError("leds muss mindestens 1 sein")
        if not 0 <= first_pin <= 22:
            raise ValueError("Ungueltiger Startpin fuer 8 zusammenhaengende GPIOs")
        if not 0 <= sm_id <= 7:
            raise ValueError("sm_id muss 0..7 sein")

        self.leds = int(leds)
        self.brightness = max(0, min(255, int(brightness)))
        self.yield_every = max(1, int(yield_every))
        self.reset_ms = max(1, (int(reset_us) + 999) // 1000)

        # Zwei logische Frames: je 8 Kanaele mit je leds GRB-Woertern.
        self._frames = [
            [array("I", [0]) * self.leds for _ in range(CHANNELS)],
            [array("I", [0]) * self.leds for _ in range(CHANNELS)],
        ]
        # Zwei Sende-Puffer: 24 Masken/LED, vier Masken je 32-Bit-Wort.
        self._tx = [
            array("I", [0]) * (self.leds * 6),
            array("I", [0]) * (self.leds * 6),
        ]
        self._draw = 0
        self._spare_tx = 0
        self._send_tx = None
        self._lock = asyncio.Lock()

        self.sm_id = int(sm_id)
        self.sm = rp2.StateMachine(
            self.sm_id, ws2812_parallel8, freq=8_000_000,
            out_base=Pin(first_pin)
        )
        self.sm.active(1)

        self.dma = rp2.DMA()
        pio_num = self.sm_id >> 2
        local_sm = self.sm_id & 3
        dreq = (pio_num << 3) + local_sm
        self._dma_ctrl = self.dma.pack_ctrl(
            size=2, inc_read=True, inc_write=False, treq_sel=dreq
        )

    def _grb(self, rgb):
        r, g, b = rgb
        br = self.brightness
        r = (max(0, min(255, int(r))) * br) // 255
        g = (max(0, min(255, int(g))) * br) // 255
        b = (max(0, min(255, int(b))) * br) // 255
        return (g << 16) | (r << 8) | b

    @property
    def drawing_frame(self):
        return self._frames[self._draw]

    def pixel(self, channel, index, rgb=None):
        if not 0 <= channel < CHANNELS:
            raise IndexError("channel muss 0..7 sein")
        if not 0 <= index < self.leds:
            raise IndexError("LED-Index ungueltig")
        frame = self._frames[self._draw]
        if rgb is None:
            v = frame[channel][index]
            return ((v >> 8) & 255, (v >> 16) & 255, v & 255)
        frame[channel][index] = self._grb(rgb)

    def fill(self, channel, rgb):
        if not 0 <= channel < CHANNELS:
            raise IndexError("channel muss 0..7 sein")
        value = self._grb(rgb)
        dst = self._frames[self._draw][channel]
        for i in range(self.leds):
            dst[i] = value

    def fill_all(self, rgb):
        value = self._grb(rgb)
        frame = self._frames[self._draw]
        for ch in range(CHANNELS):
            dst = frame[ch]
            for i in range(self.leds):
                dst[i] = value

    def clear(self):
        frame = self._frames[self._draw]
        for ch in range(CHANNELS):
            dst = frame[ch]
            for i in range(self.leds):
                dst[i] = 0

    async def _encode(self, frame_index, tx_index):
        """Frame kooperativ in parallele 8-Bit-Bitplanes umwandeln."""
        frame = self._frames[frame_index]
        tx = self._tx[tx_index]
        oi = 0
        word = 0
        byte_pos = 0

        for led in range(self.leds):
            for bit in range(23, -1, -1):
                test = 1 << bit
                mask = 0
                for ch in range(CHANNELS):
                    if frame[ch][led] & test:
                        mask |= 1 << ch
                word |= mask << (byte_pos * 8)
                byte_pos += 1
                if byte_pos == 4:
                    tx[oi] = word
                    oi += 1
                    word = 0
                    byte_pos = 0
            if (led + 1) % self.yield_every == 0:
                await asyncio.sleep_ms(0)

    async def wait(self):
        """Kooperativ warten, bis DMA und WS2812-Latch abgeschlossen sind."""
        if self._send_tx is None:
            return
        while self.dma.active():
            await asyncio.sleep_ms(0)
        await asyncio.sleep_ms(self.reset_ms)
        self._send_tx = None

    async def show(self, copy=True):
        """Aktuellen Zeichenpuffer senden und sofort einen neuen freigeben.

        Die Bitplane-Konvertierung gibt regelmaessig an uasyncio ab. Falls der
        vorige DMA-Frame noch laeuft, wird dessen Ende erst nach der Konvertierung
        abgewartet. copy=True kopiert den gesendeten Frame als Ausgangspunkt in
        den neuen Zeichenpuffer. copy=False ist schneller fuer komplett neu
        gezeichnete Frames.
        """
        async with self._lock:
            encode_frame = self._draw
            encode_tx = self._spare_tx

            # Solange der vorige TX-Puffer vom DMA gelesen wird, kann bereits
            # der andere TX-Puffer aufgebaut werden.
            await self._encode(encode_frame, encode_tx)
            await self.wait()

            # DMA liest nun encode_tx; der andere TX-Puffer wird frei.
            self.dma.config(
                read=self._tx[encode_tx], write=self.sm,
                count=len(self._tx[encode_tx]),
                ctrl=self._dma_ctrl, trigger=True
            )
            self._send_tx = encode_tx
            self._spare_tx = 1 - encode_tx

            # Auf den zweiten logischen Frame wechseln.
            new_draw = 1 - encode_frame
            if copy:
                src = self._frames[encode_frame]
                dst = self._frames[new_draw]
                for ch in range(CHANNELS):
                    for i in range(self.leds):
                        dst[ch][i] = src[ch][i]
                    await asyncio.sleep_ms(0)
            self._draw = new_draw

    async def blackout(self):
        self.clear()
        await self.show(copy=False)
        await self.wait()

    async def deinit(self, blackout=True):
        async with self._lock:
            await self.wait()
            if blackout:
                self.clear()
                await self._encode(self._draw, self._spare_tx)
                self.dma.config(
                    read=self._tx[self._spare_tx], write=self.sm,
                    count=len(self._tx[self._spare_tx]),
                    ctrl=self._dma_ctrl, trigger=True
                )
                self._send_tx = self._spare_tx
                await self.wait()
            self.sm.active(0)
            self.dma.close()
