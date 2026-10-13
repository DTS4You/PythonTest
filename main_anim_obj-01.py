###############################################################################
### Name    : main_anim_obj-01
### Version : 0.99
###############################################################################
#import uasyncio as asyncio             # MicroPython RP2040
import asyncio                          # Python 3.x

import libs.modul_anim_obj as myanim

TIME_BACKGROUND_TASK    = 1
TIME_MAIN_LOOP          = 0.3

#------------------------------------------------------------------------------
# --- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    """Simuliert eine parallele Hardware-Aufgabe (z.B. Status-LED blinken)"""
    print("Starte Hintergrund-Task: Status-LED blinken...")
    
    while True:
        print(f"Loop: Hintergrund-Task läuft...")
        await asyncio.sleep(TIME_BACKGROUND_TASK)    # Kurze Pause, um die CPU nicht zu blockieren

#------------------------------------------------------------------------------
# Main-Loop als asynchroner Task
#------------------------------------------------------------------------------
async def main_loop():

    while True:
        #if hwdebug.read_input():
        #    hwdebug.write_output(1)            # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED einzuschalten
        #else:
        #    #hwdebug.write_output(0)           # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED auszuschalten
        pass

        await asyncio.sleep(TIME_MAIN_LOOP)       # Kurze Pause, um die CPU nicht zu blockieren
#------------------------------------------------------------------------------

def anim_setup():

    debug_anim  = True
    debug_color = True
    debug_fill  = False

    print("--- Start Color Test ---")
    color_file = "cfg_colors.json"
    color_index = myanim.load_or_create_colors(color_file)
    print("Farbenindex erzeugt")
    if debug_color:
        print("\n--- Test COLOR_OBJ ---")
        for obj in color_index:
            print(f"Index: {obj.id:2d}, R: {obj.red:3d}, G: {obj.green:3d}, B: {obj.blue:3d}, Brightness: {obj.brightness}, RGB32: {hex(obj.rgb32)}")
        print("\n--- Test int32_to_4bytes ---")
        for obj in color_index:
            b0, b1, b2, b3 = myanim.int32_to_4bytes(obj.rgb32, little_endian=True)
            print(f"Index: {obj.id:2d}, RGB32: {hex(obj.rgb32)}, Bytes: [{b0:3d}, {b1:3d}, {b2:3d}, {b3:3d}]")
        print("Farbenindex 2 ist Farbe: ", color_index[2].rgb32)
    print("--- Ende Color Test ---")

    #--------------------------------------------------------------------------
    print("--- Start Animation Test ---")
    print("-> Config-Dateien setzen")
    patterns_file = "cfg_patterns.json"                         # Pattern-Datei, die eingelsen wird.
    objects_file = "cfg_anim_objects.json"                      # Objekt-Datei, die eingelesen wird.
    anim_pattern = myanim.load_or_create_patterns(patterns_file)
    print("--> Patterns erzeugt")
    anim_obj = myanim.load_or_create_objects(objects_file, anim_pattern, color_index)
    print("--> Objekte erzeugt")
    #--------------------------------------------------------------------------
    print("Anzahl der LED-Objekte: ", len(anim_obj))


#------------------------------------------------------------------------------
# --- Alle Tasks starten ---
#-----------------------------------------------------------------------------
async def main():
    anim_setup()
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