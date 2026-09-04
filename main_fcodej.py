###############################################################################
### V 1.00
###############################################################################
#import uasyncio as asyncio              # MicroPython RP2040
import asyncio                         # Python 3.11
import json

#==============================================================================
# Globales Dictionary für die Konfigurationswerte
CONFIG = {}

def load_global_config(filepath="config.json"):
    """
    Liest die JSON-Datei ein und befüllt das globale CONFIG-Dictionary.
    Einschließlich Fallbacks bei Dateifehlern.
    """
    global CONFIG
    
    # Standardwerte (Fallbacks), falls die JSON-Datei fehlt oder unvollständig ist
    defaults = {
        "frame_time": 20,
        "blink_time": 500,
        "board_modus": "Master",
        "load_modul_hwdebug": False,
        "load_modul_anim_obj": True,
        "load_modul_fcode": True
    }
    
    try:
        with open(filepath, "r") as f:
            loaded_data = json.load(f)
            defaults.update(loaded_data)
            print(f"[CONFIG] '{filepath}' erfolgreich geladen.")
    except (OSError, ValueError) as e:
        print(f"[CONFIG] Fehler beim Laden von '{filepath}': {e}. Nutze Standardwerte.")
    
    CONFIG = defaults
#==============================================================================

# --- 1. KONFIGURATION BEIM START LADEN ---
load_global_config("cfg_global.json")

# --- 2. OPTIONALE MODUL-STEUERUNG ---
if CONFIG["load_modul_hwdebug"]:
    print("[INIT] -> Modul Hardware-Debug wird geladen...")
    global hwdebug
    import libs.module_hwdebug as myhwdebug
    hwdebug = myhwdebug.HWDEBUG()
else:
    print("[INIT] ## Modul Hardware-Debug wird nicht geladen ##")

if CONFIG["load_modul_anim_obj"]:
    print("[INIT] -> Modul Animationsobjekte wird geladen...")
    global anim_obj
    import libs.modul_anim_obj as myanim
    patterns_file   = "cfg_patterns.json"
    objects_file    = "cfg_anim_objects.json"
    # 1. Zuerst Patterns laden
    anim_pattern = myanim.load_or_create_patterns(patterns_file)
    # 2. Dann Animationsobjekte laden und mit den loaded Patterns verknüpfen
    anim_obj = myanim.load_or_create_objects(objects_file, anim_pattern)
else:
    print("[INIT] ## Modul Animationsobjekte wird nicht geladen ##")

if CONFIG["load_modul_fcode"]:
    print("[INIT] -> Modul F-Code wird geladen...")
    global fcode_array
    import libs.modul_fcode as myfcode
    filepath = "cfg_fcode_array.json"
    fcode_array = myfcode.load_or_create_json(filepath)
else:
    print("[INIT] ## Modul F-Code wird nicht geladen ##")


def new_input_action():
    print("Anzahl der LED-Objekte: ",len(anim_obj))
    for i in range(len(anim_obj)):
        print("Loop: ", i)

#------------------------------------------------------------------------------
# --- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    """Simuliert eine parallele Hardware-Aufgabe (z.B. Status-LED blinken)"""
    print("Starte Hintergrund-Task: Status-LED blinken...")
    print(f"Blink_Time: {CONFIG["blink_time"]}")
    blink_state = False
    while True:
        #hwdebug.write_output(blink_state)      # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED zu blinken
        blink_state = not blink_state
        print("Blink....Blink")
        #print(myfcode.get_array_from_obj(fcode_array, 1))
        new_input_action()
        await asyncio.sleep(CONFIG["blink_time"]/1000)  # Kurze Pause, um die CPU nicht zu blockieren

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

        await asyncio.sleep(CONFIG["blink_time"]/1000)  # Kurze Pause, um die CPU nicht zu blockieren
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
        #hwdebug.write_output(0)    # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED auszuschalten
        print("Programm wurde durch Benutzer abgebrochen.")
        #machine.reset()            # Nur bei MicroPython auf dem RP2040 aktivieren, um den Controller neu zu starten
#------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# --- Start bei Main-Aufruf
# ------------------------------------------------------------------------------

if __name__ == "__main__":

    pre_main()      # Start der Pre-Main-Funktion

# =============================================================================