import array
import time
import math
from machine import Pin, mem32
import rp2
import uctypes

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, 
             autopull=True, pull_thresh=24)
def ws2812_parallel():
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0) [2]
    jmp(not_x, "do_zero")   .side(1) [1]
    jmp("bitloop")          .side(1) [4]
    label("do_zero")
    nop()                   .side(0) [4]
    wrap()

class WS2812DoubleBuffered:
    def __init__(self, start_pin, leds_per_strip):
        self.num_strips = 8
        self.leds_per_strip = leds_per_strip
        self.DMA_BASE = 0x50000000
        
        # Erzeuge ZWEI Sätze von Buffern (Double Buffering)
        # buffer_set[0] = Front-Buffer (wird gesendet)
        # buffer_set[1] = Back-Buffer (wird beschrieben)
        self.buffer_sets = [
            [array.array("I", [0] * leds_per_strip) for _ in range(8)],
            [array.array("I", [0] * leds_per_strip) for _ in range(8)]
        ]
        
        self.write_index = 0  # Welchen Buffer beschreibt die CPU gerade
        self.dma_configs = [0] * 8
        
        # Initialisierung der PIOs und DMA-Grundkonfiguration
        for i in range(8):
            pin = Pin(start_pin + i)
            sm = rp2.StateMachine(i, ws2812_parallel, freq=8_000_000, sideset_base=pin)
            sm.active(1)
            
            # DREQ Auswahl (PIO0 oder PIO1)
            dreq = i if i < 4 else 8 + (i - 4)
            self.dma_configs[i] = (dreq << 15) | (1 << 4) | (2 << 2) | 1
            
            # Ziel-Adresse (FIFO) festlegen
            dest_fifo = (0x50200010 + (i * 4)) if i < 4 else (0x50300010 + ((i - 4) * 4))
            mem32[self.DMA_BASE + (i * 0x40) + 0x04] = dest_fifo

    def set_pixel(self, strip, index, r, g, b):
        """ Schreibt immer in den aktuellen Back-Buffer """
        # WS2812: GRB Format
        self.buffer_sets[self.write_index][strip][index] = (g << 24) | (r << 16) | (b << 8)

    def is_sending(self):
        """ Prüft, ob einer der DMA Kanäle noch aktiv ist """
        for i in range(8):
            if mem32[self.DMA_BASE + (i * 0x40) + 0x0C] & (1 << 24):
                return True
        return False

    def show(self):
        # 1. Warten, bis der vorherige DMA-Transfer fertig ist
        while self.is_sending():
            pass
        
        # 2. Reset-Pause für die LEDs (Timing-Sicherheit)
        time.sleep_us(300)
        
        # 3. Den aktuellen Back-Buffer zum Senden (Front-Buffer) machen
        read_index = self.write_index
        
        # 4. Alle 8 DMA Kanäle mit dem gewählten Buffer-Set triggern
        for i in range(8):
            base = self.DMA_BASE + (i * 0x40)
            mem32[base + 0x00] = uctypes.addressof(self.buffer_sets[read_index][i])
            mem32[base + 0x08] = self.leds_per_strip
            mem32[base + 0x0C] = self.dma_configs[i]
            
        # 5. Den Back-Buffer umschalten (0 -> 1 oder 1 -> 0)
        # Die CPU schreibt ab jetzt in den jeweils anderen Buffer
        self.write_index = 1 - self.write_index

# --- Anwendung ---

num_leds    = 100

# 8 Streifen à 250 LEDs, Start an GPIO 2 (um UART Konflikte zu vermeiden)
leds = WS2812DoubleBuffered(start_pin=2, leds_per_strip=num_leds)

# Pre-calculated Sinus Lookup Table (256 Werte von 0 bis 255 skaliert)
SIN_TABLE = array.array("b", [int(math.sin(i * 2 * math.pi / 256) * 127) for i in range(256)])

# Native Decorator zwingt MicroPython, Maschinencode zu generieren
@micropython.native
def render_frame(leds_obj, t_int):
    # Lokale Referenzen für schnellen Zugriff in der Schleife
    sin_tab = SIN_TABLE
    set_px = leds_obj.set_pixel
    
    for y in range(8):
        y_off = y * 20
        for x in range(250):
            # Schnelle Integer-Arithmetik statt Fließkomma-Mathe
            idx1 = (x * 3 + t_int) & 255
            idx2 = (y_off + t_int * 2) & 255
            idx3 = (x + y * 10 - t_int) & 255
            
            # Werte aus der Lookup-Tabelle holen (-127 bis 127)
            val1 = sin_tab[idx1]
            val2 = sin_tab[idx2]
            val3 = sin_tab[idx3]
            
            # Plasma-Wert zusammenbauen (0 bis 255)
            plasma = (val1 + val2 + val3 + 381) // 3
            
            # Schnelles Farb-Mapping ohne Fließkommazahlen
            r = (sin_tab[(plasma + t_int) & 255] + 128) >> 4  # Max Helligkeit ~16
            g = (sin_tab[(plasma * 2 - t_int) & 255] + 128) >> 5
            b = (sin_tab[(plasma + y_off) & 255] + 128) >> 4
            
            set_px(y, x, r, g, b)

# --- Hauptschleife ---
leds = WS2812DoubleBuffered(start_pin=2, leds_per_strip=num_leds)

frame_time  = 0.01
t_counter   = 0

try:
    print("Starte native-optimierte Plasma-Animation...")
    while True:
        #render_frame(leds, t_counter)
        #leds.show()
        #t_counter = (t_counter + 2) & 255
        for y in range(8):
            for x in range(num_leds): leds.set_pixel(y, x, 0, 0, 0)
        leds.show()
        time.sleep(frame_time)
        for y in range(8):
            for x in range(num_leds): leds.set_pixel(y, x, 30, 30, 30)
        leds.show()
        time.sleep(frame_time)
        
except KeyboardInterrupt:
    for y in range(8):
        for x in range(num_leds): leds.set_pixel(y, x, 0, 0, 0)
    leds.show()

