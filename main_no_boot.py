###############################################################################
### V 1.00
###############################################################################
import uasyncio as asyncio
import libs.modul_config as mycfg

load_modul_hwdebug      = True
load_modul_anim_obj     = True
load_modul_color_index  = True
 

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

def import_modul_color_index():
    global color_index
    import libs.modul_color_index as mycolor
    filepath = "cfg_colors.json"
    color_index = mycolor.load_or_create_colors(filepath)

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
        await asyncio.sleep_ms(mycfg.blink_time)

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
        hwdebug.write_output(0)
        print("Programm wurde durch Benutzer abgebrochen.")
        machine.reset()
#------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# --- Start bei Main-Aufruf
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    mycfg.load_config()
    if load_modul_hwdebug:
        import_module_hwdebug()
    if load_modul_anim_obj:
        import_modul_anim_obj()
    if load_modul_color_index:
        import_modul_color_index()

    pre_main()      # Start der Pre-Main-Funktion

# =============================================================================