###############################################################################
### V 1.00
###############################################################################
import uasyncio as asyncio              # MicroPython RP2040
#import asyncio                         # Python 3.11
import libs.modul_config as mycfg

load_modul_hwdebug      = True
load_modul_anim_obj     = True

def import_module_hwdebug():
    global hwdebug
    import libs.module_hwdebug as myhwdebug
    hwdebug = myhwdebug.HWDEBUG()

def import_modul_anim_obj():
    global anim_obj
    import libs.modul_anim_obj as myanim
    patterns_file   = "cfg_patterns.json"
    objects_file    = "cfg_anim_objects.json"
    # 1. Zuerst Patterns laden
    anim_pattern = myanim.load_or_create_patterns(patterns_file)
    # 2. Dann Animationsobjekte laden und mit den loaded Patterns verknüpfen
    anim_obj = myanim.load_or_create_objects(objects_file, anim_pattern)

#------------------------------------------------------------------------------
# --- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    """Simuliert eine parallele Hardware-Aufgabe (z.B. Status-LED blinken)"""
    print("Starte Hintergrund-Task: Status-LED blinken...")
    print(f"Blink_Time: {mycfg.blink_time}")
    blink_state = False
    while True:
        hwdebug.write_output(blink_state)      # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED zu blinken
        blink_state = not blink_state
        await asyncio.sleep_ms(mycfg.blink_time)  # Kurze Pause, um die CPU nicht zu blockieren

#------------------------------------------------------------------------------
# Main-Loop als asynchroner Task
#------------------------------------------------------------------------------
async def main_loop():

    while True:
        #if hwdebug.read_input():
        #    hwdebug.write_output(1)            # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED einzuschalten
        #else:
        #    #hwdebug.write_output(0)           # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED auszuschalten
        #    pass

        await asyncio.sleep_ms(mycfg.frame_time)  # Kurze Pause, um die CPU nicht zu blockieren
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
def pre_main():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        hwdebug.write_output(0)    # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED auszuschalten
        print("Programm wurde durch Benutzer abgebrochen.")
        machine.reset()            # Nur bei MicroPython auf dem RP2040 aktivieren, um den Controller neu zu starten
#------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# --- Start bei Main-Aufruf
# ------------------------------------------------------------------------------

if __name__ == "__main__":

    mycfg.load_config()             # Lade Konfiguration aus cfg_config.json

    if load_modul_hwdebug:
        import_module_hwdebug()
    if load_modul_anim_obj:
        import_modul_anim_obj()

    pre_main()      # Start der Pre-Main-Funktion

# =============================================================================