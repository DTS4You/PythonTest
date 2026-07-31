###############################################################################
### Programm    : WS2812 Fast DMA + Viper
### Version     : 0.99
### Autor       : Norbert Schwarz
### Datum       : 2026-07-31
###############################################################################
#import sys
import array
import time
import math
from machine import Pin, mem32
import rp2
import uctypes
import uasyncio as asyncio

#------------------------------------------------------------------------------
frame_time = 0.3  # Zeit in Sekunden zwischen den Frames
#------------------------------------------------------------------------------
led_board       = Pin(25, Pin.OUT)
switch_board    = Pin(24, Pin.IN, Pin.PULL_UP)
switch_extern   = Pin(17, Pin.IN, Pin.PULL_UP)
#------------------------------------------------------------------------------



print("Programmstart")
led_board.value(0)
time.sleep(0.3)
while(switch_board.value()):
    #print("Warte auf Taste")
    time.sleep(0.3)

led_board.value(1)

print("Starte Viper-beschleunigte Berechnung...")



try:
    while True:
        # Aktuelle Adressen des Ziel-Buffers holen
        if leds.write_index == 0:
            addrs_ptr = uctypes.addressof(leds.addrs_set0)
        else:
            addrs_ptr = uctypes.addressof(leds.addrs_set1)
            
        leds.fill()
        leds.show()
        time.sleep(frame_time)
        leds.clear()
        leds.show()
        time.sleep(frame_time)
        
except KeyboardInterrupt:
    leds.clear()
    leds.show()
    leds.cleanup()
    del leds
    led_board.value(0)
    print("ENDE")
    machine.reset()

