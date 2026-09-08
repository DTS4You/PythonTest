import array
import time
from machine import Pin, mem32
import rp2
import uctypes

LEDS_PER_STRIP = 200
NUM_STRIPS = 8

# --- 1. PIO ASSEMBLY FÜR 8 PARALLELE PINS ---
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,) * 8, 
             out_shiftdir=rp2.PIO.SHIFT_LEFT, 
             autopull=True, 
             pull_thresh=32)
def ws2812_parallel_8chan():
    wrap_target()
    label("bitloop")
    
    # 1. Alle 8 Pins auf HIGH ziehen (3 Zyklen = 375 ns)
    mov(pins, osr)          .side(0) [0] # Nutzt ein 'all-ones' Register oder High-Maske
    # Für sauberes Out-Pulse-Handling nutzen wir Set/Out:
    
    # Einfachere & extrem stabile Variante:
    # Wir schieben 8 Bit Daten aus dem OSR an die Pins
    out(pins, 8)            [2] # 3 Zyklen: 8 Pins bekommen Daten-Bit (High oder Low)
    
    # Ausführung des 8-Kanal Timings:
    # T1: 8 Pins HIGH
    # T2: 8 Pins halten Daten-Bit
    # T3: 8 Pins LOW
    wrap()


# Da die PIO out(pins, 8) nutzt, bauen wir eine exakte 8-Kanal Parallel-PIO:
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,) * 8, 
             out_shiftdir=rp2.PIO.SHIFT_LEFT, 
             autopull=True, 
             pull_thresh=32)
def ws2812_8x_parallel():
    wrap_target()
    # T1: Alle Pins HIGH (3 Zyklen = 375 ns)
    # Wir nutzen den mov-Befehl mit einer Alias-Zero/One Maske
    # Oder einfacher: Out liest Daten direkt aus Puffer
    
    # Zyklus 1..3: Pins HIGH
    set(pins, 0xFF)         [2] 
    
    # Zyklus 4..6: 8 Bits Daten auf die 8 Pins ausgeben
    out(pins, 8)            [2] 
    
    # Zyklus 7..10: Alle Pins LOW (4 Zyklen = 500 ns)
    set(pins, 0x00)         [3] 
    wrap()


# --- 2. FAST BIT-TRANSPOSITION (VIPER) ---
@micropython.viper
def transpose_8strips(framebuf_ptr: ptr8, dma_buf_ptr: ptr32, leds_per_strip: int):
    """
    Wandelt 8 getrennte LED-Puffer (G-R-B) in ein bit-interleaved Format um,
    das die PIO direkt per out(pins, 8) an die Pins 0..7 ausgeben kann.
    """
    dma_idx = 0
    # 24 Bits pro LED (8 Bit G, 8 Bit R, 8 Bit B)
    for led in range(leds_per_strip):
        for bit_idx in range(24):
            bit_mask = 1 << (23 - bit_idx)
            out_byte = 0
            
            # Sammle Bit N von allen 8 Strängen
            for strip in range(8):
                # Puffer-Offset für Strang `strip`, LED `led`
                strip_offset = (strip * leds_per_strip + led) * 3
                
                # 24-Bit Farbwert lesen (GRB)
                g = int(framebuf_ptr[strip_offset])
                r = int(framebuf_ptr[strip_offset + 1])
                b = int(framebuf_ptr[strip_offset + 2])
                color24 = (g << 16) | (r << 8) | b
                
                if (color24 & bit_mask) != 0:
                    out_byte |= (1 << strip)
            
            # Schreiben in DMA-Puffer (32 Bit Wort enthält 4x 8-Bit Schritte)
            # Um Speicher zu sparen, verpacken wir 4 Daten-Bytes in ein 32-Bit Wort
            shift_pos = (3 - (dma_idx & 3)) * 8
            if (dma_idx & 3) == 0:
                dma_buf_ptr[dma_idx >> 2] = out_byte << shift_pos
            else:
                dma_buf_ptr[dma_idx >> 2] |= out_byte << shift_pos
                
            dma_idx += 1


# --- 3. TREIBER-KLASSE ---
class WS2812_8Parallel:
    def __init__(self, base_pin_num: int, leds_per_strip: int):
        self.leds_per_strip = leds_per_strip
        self.num_strips = 8
        self.base_pin = Pin(base_pin_num)
        
        # Pins initialisieren (8 aufeinanderfolgende GPIOs, z.B. GP2 bis GP9)
        self.pins = [Pin(base_pin_num + i, Pin.OUT) for i in range(8)]
        
        # 1. Logischer Framebuffer: 8 Stränge * 200 LEDs * 3 Bytes (RGB)
        self.framebuffer = bytearray(8 * leds_per_strip * 3)
        
        # 2. DMA-Puffer für Transposition: 
        # 200 LEDs * 24 Bits = 4800 Bytes / 4 = 1200x 32-Bit Worte
        dma_words = (leds_per_strip * 24 + 3) // 4
        self.dma_buffer = array.array("I", [0] * dma_words)
        
        # PIO StateMachine initialisieren (auf 8 MHz)
        self.sm = rp2.StateMachine(
            0, 
            ws2812_8x_parallel, 
            freq=8_000_000, 
            out_base=self.pins[0],
            set_base=self.pins[0]
        )
        self.sm.active(1)
        
        # DMA-Kanal einrichten
        self.dma_chan = 0
        self.DMA_BASE = 0x50000000

    def set_pixel(self, strip: int, led: int, r: int, g: int, b: int):
        """Setzt eine LED auf einem bestimmten Strang (0..7)."""
        if 0 <= strip < 8 and 0 <= led < self.leds_per_strip:
            offset = (strip * self.leds_per_strip + led) * 3
            self.framebuffer[offset] = g
            self.framebuffer[offset + 1] = r
            self.framebuffer[offset + 2] = b

    def show(self):
        # 1. Bit-Plane Transposition ausführen (Viper-Speed)
        fb_ptr = uctypes.addressof(self.framebuffer)
        dma_ptr = uctypes.addressof(self.dma_buffer)
        transpose_8strips(fb_ptr, dma_ptr, self.leds_per_strip)
        
        # 2. Warten, falls letzter DMA noch läuft
        base = self.DMA_BASE + (self.dma_chan * 0x40)
        while mem32[base + 0x0C] & (1 << 24): # BUSY
            pass
            
        # Latch-Zeit (>280µs)
        time.sleep_us(300)
        
        # 3. DMA starten (1 Kanal schiebt alle Daten in SM 0 FIFO)
        dest_fifo = 0x50200010 # PIO0 TX FIFO 0
        
        mem32[base + 0x00] = dma_ptr                           # Read Addr
        mem32[base + 0x04] = dest_fifo                          # Write Addr
        mem32[base + 0x08] = len(self.dma_buffer)               # Transfer Count
        # Control: DREQ PIO0_TX0 (0), INCR_READ, 32-Bit, ENABLE
        mem32[base + 0x0C] = (0 << 15) | (1 << 4) | (2 << 2) | 1 # Trigger!


# --- TESTANWENDUNG ---
# Nutzt GPIO 2, 3, 4, 5, 6, 7, 8, 9 als Ausgänge für die 8 Stränge
matrix = WS2812_8Parallel(base_pin_num=2, leds_per_strip=200)

# Setze auf allen 8 Strängen die ersten 10 LEDs in verschiedenen Farben
for strip in range(8):
    for led in range(10):
        if strip % 2 == 0:
            matrix.set_pixel(strip, led, r=50, g=0, b=0)  # Rot auf geraden Strängen
        else:
            matrix.set_pixel(strip, led, r=0, g=0, b=50)  # Blau auf ungeraden Strängen

# Anzeigen
matrix.show()

