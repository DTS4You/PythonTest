###############################################################################
### WS2812 Viper
### V 1.00
###############################################################################
from machine import Pin
import uasyncio as asyncio
import libs.module_ws2812_dma as myws2812
import libs.module_hwdebug as myhwdebug

global hwdebug
hwdebug = myhwdebug.HWDEBUG()
global ws2812
leds = myws2812.WS2812Fast(start_pin=2, leds_per_strip=250)

#------------------------------------------------------------------------------
# --- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    print("Starte Background Task...")
    blink_time = 0.5
    blink_state = False

    while True:
        #print("Hintergrund-Task: Status-LED blinken")
        hwdebug.write_output(blink_state)
        blink_state = not blink_state
        await asyncio.sleep(blink_time)

#------------------------------------------------------------------------------
# Main-Loop als asynchroner Task
#------------------------------------------------------------------------------
async def main_loop():

    frame_time = 0.04
    print("Starte Viper-beschleunigte Berechnung...")
    while True:
        # Aktuelle Adressen des Ziel-Buffers holen
        if leds.write_index == 0:
            addrs_ptr = uctypes.addressof(leds.addrs_set0)
        else:
            addrs_ptr = uctypes.addressof(leds.addrs_set1)
        #----------------------------------------------------------------------    
        leds.fill()
        leds.show()
        await asyncio.sleep(frame_time)
        leds.clear()
        leds.show()
        await asyncio.sleep(frame_time)
        #await asyncio.sleep(0.05)  # Kurze Pause, um die CPU nicht zu blockieren
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# --- Alle Tasks starten ---
#-----------------------------------------------------------------------------
async def main():
    print("Starte Main-Loop und Hintergrund-Task...")

    await asyncio.gather(
        main_loop(),
        background_heartbeat()
    )
#------------------------------------------------------------------------------
#--- Ab hier startet das Programm
#-----------------------------------------------------------------------------
try:
    asyncio.run(main())
except KeyboardInterrupt:
    hwdebug.write_output(0)
    print("Programm wurde durch Benutzer abgebrochen.")
    leds.clear()
    leds.show()
    leds.cleanup()
    del leds
    machine.reset()
#------------------------------------------------------------------------------
