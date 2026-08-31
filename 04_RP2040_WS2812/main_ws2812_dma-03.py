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

class WS2812Fast:
    def __init__(self, start_pin, leds_per_strip):
        self.num_strips = 8
        self.leds_per_strip = leds_per_strip
        self.DMA_BASE = 0x50000000
        
        # Sätze von Buffern
        self.buffer_sets = [
            [array.array("I", [0] * leds_per_strip) for _ in range(8)],
            [array.array("I", [0] * leds_per_strip) for _ in range(8)]
        ]
        
        # Zeiger (Memory-Adressen) auf die einzelnen Arrays für superschnellen Viper-Zugriff
        self.addrs_set0 = array.array("I", [uctypes.addressof(b) for b in self.buffer_sets[0]])
        self.addrs_set1 = array.array("I", [uctypes.addressof(b) for b in self.buffer_sets[1]])
        
        self.write_index = 0
        self.dma_configs = array.array("I", [0] * 8)
        
        for i in range(8):
            pin = Pin(start_pin + i)
            sm = rp2.StateMachine(i, ws2812_parallel, freq=8_000_000, sideset_base=pin)
            sm.active(1)
            
            dreq = i if i < 4 else 8 + (i - 4)
            self.dma_configs[i] = (dreq << 15) | (1 << 4) | (2 << 2) | 1
            
            dest_fifo = (0x50200010 + (i * 4)) if i < 4 else (0x50300010 + ((i - 4) * 4))
            mem32[self.DMA_BASE + (i * 0x40) + 0x04] = dest_fifo

    def show(self):
        # Warten, falls DMA noch liest
        for i in range(8):
            while mem32[self.DMA_BASE + (i * 0x40) + 0x0C] & (1 << 24):
                pass
        
        time.sleep_us(300) # Reset Pause
        
        read_idx = self.write_index
        active_buffers = self.buffer_sets[read_idx]
        
        # Trigger DMA
        for i in range(8):
            base = self.DMA_BASE + (i * 0x40)
            mem32[base + 0x00] = uctypes.addressof(active_buffers[i])
            mem32[base + 0x08] = self.leds_per_strip
            mem32[base + 0x0C] = self.dma_configs[i]
            
        self.write_index = 1 - self.write_index

# Globaler Lookup-Table für Sinus
SIN_TABLE = array.array("b", [int(math.sin(i * 2 * math.pi / 256) * 127) for i in range(256)])

# --- DER TURBO-RENDERER (VIPER) ---
@micropython.viper
def render_viper(strip_addrs_ptr: ptr32, sin_tab_ptr: ptr8, t_int: int, leds_per_strip: int):
    # In Viper greifen wir direkt per RAW-32-Bit-Pointer auf den RAM zu
    for s in range(8):
        # Hole die Basisadresse für den aktuellen Streifen
        buf_ptr = ptr32(strip_addrs_ptr[s])
        s_off = s * 20
        
        for i in range(leds_per_strip):
            # Schnelle Math-Indices
            idx1 = (i * 3 + t_int) & 255
            idx2 = (s_off + t_int * 2) & 255
            
            val1 = int(sin_tab_ptr[idx1])
            val2 = int(sin_tab_ptr[idx2])
            
            plasma = (val1 + val2 + 254) >> 1
            
            # RGB Werte berechnen
            r = (int(sin_tab_ptr[(plasma + t_int) & 255]) + 128) >> 4
            g = (int(sin_tab_ptr[(plasma * 2) & 255]) + 128) >> 5
            b = (int(sin_tab_ptr[(plasma + s_off) & 255]) + 128) >> 4
            
            # WS2812 GRB Format als 32-Bit Integer zusammensetzen
            # Schreibt DIREKT in den RAM ohne Methodenaufruf!
            buf_ptr[i] = (g << 24) | (r << 16) | (b << 8)


# --- Hauptschleife ---
leds = WS2812Fast(start_pin=2, leds_per_strip=250)
t_counter = 0

# Zeiger vorbereiten
sin_ptr = uctypes.addressof(SIN_TABLE)

print("Starte Viper-beschleunigte Berechnung...")

try:
    while True:
        # Aktuelle Adressen des Ziel-Buffers holen
        if leds.write_index == 0:
            addrs_ptr = uctypes.addressof(leds.addrs_set0)
        else:
            addrs_ptr = uctypes.addressof(leds.addrs_set1)
            
        # Rendern direkt in den Speicher
        render_viper(addrs_ptr, sin_ptr, t_counter, 250)
        
        # DMA Ausführen
        leds.show()
        
        t_counter = (t_counter + 3) & 255
except KeyboardInterrupt:
    pass
