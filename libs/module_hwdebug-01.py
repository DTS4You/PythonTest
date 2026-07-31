###############################################################################
### Hardware Debug Modul
### V 1.00
###############################################################################
from machine import Pin
import uasyncio as asyncio

class HWDEBUG:
    def __init__(self):
        self.led_board      = Pin(25, Pin.OUT)
        self.switch_board   = Pin(24, Pin.IN, Pin.PULL_UP)
        self.switch_extern  = Pin(17, Pin.IN, Pin.PULL_UP)

    def read_input(self):
        return not (self.switch_board.value() and self.switch_extern.value())

    def write_output(self, value):
        self.led_board.value(value)

    
#==============================================================================
# Test-Funktion
def do_this(value):

    pass    

#------------------------------------------------------------------------------
# Main-Loop als asynchroner Task
#------------------------------------------------------------------------------
async def main_loop():

    global hwdebug

    hwdebug = HWDEBUG()

    while True:
        if hwdebug.read_input():
            do_this(1)
            hwdebug.write_output(1)
        else:
            do_this(0)
            #hwdebug.write_output(0)
        
        await asyncio.sleep(0.03)  # Kurze Pause, um die CPU nicht zu blockieren
#------------------------------------------------------------------------------

# --- Hintergrund-Task simulieren ---
async def background_heartbeat():
    """Simuliert eine parallele Hardware-Aufgabe (z.B. Status-LED blinken)"""
    blink_state = False
    while True:
        print("Hintergrund-Task: Status-LED blinken")
        hwdebug.write_output(blink_state)
        blink_state = not blink_state
        await asyncio.sleep(1)

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
    machine.reset()
#------------------------------------------------------------------------------
