import json

# Globale Variablen mit Standardwerten (Default)
frame_time = 100
blink_time = 500
board_modus = "Master"
load_modul_hwdebug = True
load_modul_anim_obj = True
load_modul_color_index = True

CONFIG_FILE = "cfg_config.json"


def save_config():
    """Speichert die aktuellen globalen Variablen formatiert in der JSON-Datei."""
    lines = [
        "{",
        f'    "frame_time": {frame_time:4d},',
        f'    "blink_time": {blink_time:4d},',
        f'    "board_modus": "{board_modus}",',
        f'    "load_modul_hwdebug": {"true" if load_modul_hwdebug else "false"},',
        f'    "load_modul_anim_obj": {"true" if load_modul_anim_obj else "false"},',
        f'    "load_modul_color_index": {"true" if load_modul_color_index else "false"}',
        "}",
    ]

    formatted_json = "\n".join(lines)

    with open(CONFIG_FILE, "w") as f:
        f.write(formatted_json)
    print(f"Konfiguration erfolgreich in '{CONFIG_FILE}' gespeichert.")


def load_config():
    """Lädt die Variablen aus der Datei und weist sie globalen Variablen zu."""
    global frame_time, blink_time, board_modus
    global load_modul_hwdebug, load_modul_anim_obj, load_modul_color_index

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)

            # Einzelne Werte den globalen Variablen zuweisen
            frame_time = data.get("frame_time", frame_time)
            blink_time = data.get("blink_time", blink_time)
            board_modus = data.get("board_modus", board_modus)
            load_modul_hwdebug = data.get(
                "load_modul_hwdebug", load_modul_hwdebug
            )
            load_modul_anim_obj = data.get(
                "load_modul_anim_obj", load_modul_anim_obj
            )
            load_modul_color_index = data.get(
                "load_modul_color_index", load_modul_color_index
            )

            print(f"Konfiguration aus '{CONFIG_FILE}' erfolgreich geladen.")
    except (OSError, ValueError):
        # OSError: Datei fehlt | ValueError: ungültiges/beschädigtes JSON
        print(
            f"Datei '{CONFIG_FILE}' nicht gefunden oder beschädigt. Erstelle Default-Konfiguration..."
        )
        save_config()

#==============================================================================
# --- Beispiel für die Nutzung ---
if __name__ == "__main__":
    # 1. Konfiguration laden
    load_config()

    # 2. Zugreifen auf globale Variablen
    print(f"frame_time = {frame_time}")
    print(f"blink_time = {blink_time}")
    print(f"board_modus = {board_modus}")

    # 3. Globale Variablen verändern (in Hauptschleife oder Funktionen)
    frame_time = 20

    # 4. Speichern
    save_config()
#==============================================================================