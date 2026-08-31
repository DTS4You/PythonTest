###############################################################################
### Hardware Debug Modul
### V 1.00
###############################################################################
from machine import Pin
import uasyncio as asyncio
import libs.module_hwdebug as myhwdebug

def init_hwdebug():
    global hwdebug
    hwdebug = myhwdebug.HWDEBUG()

#------------------------------------------------------------------------------
# --- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    """Simuliert eine parallele Hardware-Aufgabe (z.B. Status-LED blinken)"""
    blink_state = False
    while True:
        #print("Hintergrund-Task: Status-LED blinken")
        hwdebug.write_output(blink_state)
        blink_state = not blink_state
        await asyncio.sleep(1)

#------------------------------------------------------------------------------
# Main-Loop als asynchroner Task
#------------------------------------------------------------------------------
async def main_loop():

    while True:
        if hwdebug.read_input():
            hwdebug.write_output(1)
        else:
            #hwdebug.write_output(0)
            pass

        await asyncio.sleep(0.03)  # Kurze Pause, um die CPU nicht zu blockieren
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# --- Alle Tasks starten ---
#-----------------------------------------------------------------------------
async def main():
    print("Starte Main-Loop und Hintergrund-Task...")
    init_hwdebug()
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
    machine.reset()
#------------------------------------------------------------------------------
