import array
import time
from machine import Pin, mem32
import rp2
import uctypes

LEDS_PER_STRIP = 200
BASE_PIN = 2  # GP2 bis GP9

# --- 1. HARMONISIERTES PIO-PROGRAMM (8 MHz Clock = 125 ns pro Zyklus) ---
@rp2.asm_pio(
    out_init=(rp2.PIO.OUT_LOW,) * 8, 
    out_shiftdir=rp2.PIO.SHIFT_LEFT, 
    autopull=True, 
    pull_thresh=32
)
def ws2812_8x_parallel():
    # Einmalig beim Start: Register X mit 0xFFFFFFFF (alle Bits 1) füllen
    mov(x, invert(null))
    
    wrap_target()
    # T1: Alle 8 Pins gleichzeitig HIGH schalten (3 Zyklen = 375 ns)
    mov(pins, x)            [2] 
    
    # T2: 8 Datenbits aus OSR an die Pins schieben (3 Zyklen = 375 ns)
    #     - Bit 0 schaltet Pin auf LOW  --> T0H = 375 ns
    #     - Bit 1 hält Pin auf HIGH     --> T1H = 750 ns
    out(pins, 8)            [2] 
    
    # T3: Alle 8 Pins auf LOW schalten (4 Zyklen = 500 ns)
    mov(pins, null)         [3] 
    wrap()


# --- 2. FAST TRANSPOSITION (VIPER, 1 BYTE PRO BIT) ---
@micropython.viper
def transpose_8strips(framebuf_ptr: ptr8, dma_buf_ptr: ptr32, leds_per_strip: int):
    dma_word_idx = 0
    current_word = 0
    bytes_in_word = 0
    
    for led in range(leds_per_strip):
        for bit_idx in range(24):
            bit_mask = 1 << (23 - bit_idx)
            data_byte = 0
            
            # Bit N von allen 8 Strängen auf einen Schlag einsammeln
            for strip in range(8):
                strip_offset = (strip * leds_per_strip + led) * 3
                g = int(framebuf_ptr[strip_offset])
                r = int(framebuf_ptr[strip_offset + 1])
                b = int(framebuf_ptr[strip_offset + 2])
                color24 = (g << 16) | (r << 8) | b
                
                if (color24 & bit_mask) != 0:
                    data_byte |= (1 << strip)
            
            # In 32-Bit-Wort für DMA packen (MSB-first für PIO SHIFT_LEFT)
            current_word = (current_word << 8) | data_byte
            bytes_in_word += 1
            
            if bytes_in_word == 4:
                dma_buf_ptr[dma_word_idx] = current_word
                dma_word_idx += 1
                current_word = 0
                bytes_in_word = 0


# --- 3. HARDBOUND TREIBERKLASSE ---
class WS2812_8Parallel:
    def __init__(self, base_pin_num: int, leds_per_strip: int):
        self.leds_per_strip = leds_per_strip
        self.DMA_BASE = 0x50000000
        self.dma_chan = 0
        
        # MicroPython Pin-Objekte als Ausgänge initialisieren
        self.pins = [Pin(base_pin_num + i, Pin.OUT, value=0) for i in range(8)]
        
        # Puffer für RGB-Daten
        self.framebuffer = bytearray(8 * leds_per_strip * 3)
        
        # Exakte DMA-Puffergröße: 200 LEDs * 24 Bits = 4800 Bytes = 1200 Worte (32-Bit)
        dma_words = (leds_per_strip * 24) // 4
        self.dma_buffer = array.array("I", [0] * dma_words)
        
        # State Machine mit out_base verknüpfen
        self.sm = rp2.StateMachine(
            0, 
            ws2812_8x_parallel, 
            freq=8_000_000, 
            out_base=self.pins[0],
            set_base=self.pins[0]
        )
        
        # Pins in PIO als Ausgänge freischalten
        self.sm.exec("set(pindirs, 0x1F)") # Befehl setzt die ersten Pins
        for p in self.pins:
            p.init(Pin.OUT)
            
        self.sm.active(1)

    def set_pixel(self, strip: int, led: int, r: int, g: int, b: int):
        if 0 <= strip < 8 and 0 <= led < self.leds_per_strip:
            offset = (strip * self.leds_per_strip + led) * 3
            self.framebuffer[offset] = g
            self.framebuffer[offset + 1] = r
            self.framebuffer[offset + 2] = b

    def show(self):
        fb_ptr = uctypes.addressof(self.framebuffer)
        dma_ptr = uctypes.addressof(self.dma_buffer)
        
        # Transposition durchführen
        transpose_8strips(fb_ptr, dma_ptr, self.leds_per_strip)
        
        base = self.DMA_BASE + (self.dma_chan * 0x40)
        
        # Warten falls DMA noch sendet
        while mem32[base + 0x0C] & (1 << 24):
            pass
            
        # Resetsignal / Latch-Pause (>280 µs)
        time.sleep_us(300)
        
        dest_fifo = 0x50200010  # PIO0 TX FIFO 0
        dma_ctrl = (0 << 15) | (1 << 4) | (2 << 2) | 1  # DREQ PIO0_TX0, INCR_READ, 32-Bit, ENABLE
        
        # DMA Ausführung triggern
        mem32[base + 0x00] = dma_ptr
        mem32[base + 0x04] = dest_fifo
        mem32[base + 0x08] = len(self.dma_buffer)
        mem32[base + 0x0C] = dma_ctrl


# --- TESTANSTEUERUNG ---
matrix = WS2812_8Parallel(base_pin_num=BASE_PIN, leds_per_strip=LEDS_PER_STRIP)

# Testmuster setzen
for i in range(20):
    matrix.set_pixel(strip=0, led=i, r=255, g=0, b=0)   # Rot auf Strang 0 (GP2)
    matrix.set_pixel(strip=1, led=i, r=0, g=255, b=0)   # Grün auf Strang 1 (GP3)
    matrix.set_pixel(strip=7, led=i, r=0, g=0, b=255)   # Blau auf Strang 7 (GP9)

matrix.show()

