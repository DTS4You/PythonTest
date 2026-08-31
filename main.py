###############################################################################
### Hardware Debug Modul
### V 1.00
###############################################################################
import uasyncio as asyncio

load_module_hwdebug     = True
load_module_ws2812      = False
load_module_serial      = False
load_module_xgio        = False 

def import_module_hwdebug():
    global hwdebug
    import libs.module_hwdebug as myhwdebug
    hwdebug = myhwdebug.HWDEBUG()

def import_module_ws2812():
    #import libs.module_ws2812 as myws2812
    pass

def import_module_serial():
    #import libs.module_serial as myserial
    pass

def import_module_xgio():
    #import libs.module_xgio as myxgio
    pass

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
    await asyncio.gather(
        main_loop(),
        background_heartbeat()
    )
#------------------------------------------------------------------------------
#--- Ab hier startet das Programm
#-----------------------------------------------------------------------------
def main():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        hwdebug.write_output(0)
        print("Programm wurde durch Benutzer abgebrochen.")
        machine.reset()
#------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# --- Start bei Main-Aufruf
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    if load_module_hwdebug:
        import_module_hwdebug()
    if load_module_ws2812:
        import_module_ws2812()
    if load_module_serial:
        import_module_serial()
    if load_module_xgio:
        import_module_xgio()
    main()      # Start der Main-Funktion

# =============================================================================