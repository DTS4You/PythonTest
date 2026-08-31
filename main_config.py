import json

# Globale Variablen mit Standardwerten (Default)
frame_time              = 100
blink_time              = 500
board_modus             = "Master"
load_modul_hwdebug      = True
load_modul_anim_obj     = True
load_modul_color_index  = True

CONFIG_FILE = "cfg_config.json"


def save_config():
    """Speichert die aktuellen globalen Variablen in der JSON-Datei."""
    lines = [
        "{",
        f'    "frame_time": {frame_time:4d},',
        f'    "blink_time": {blink_time:4d},',
        f'    "board_modus": "{board_modus}",',
        f'    "modul_hwdebug": {"true" if load_modul_hwdebug else "false"},',
        f'    "modul_anim_obj": {"true" if load_modul_anim_obj else "false"},',
        f'    "modul_color_index": {"true" if load_modul_color_index else "false"}',
        "}"
    ]
    
    formatted_json = "\n".join(lines)
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(formatted_json)
    print(f"Konfiguration erfolgreich in '{CONFIG_FILE}' gespeichert.")


def load_config():
    """Lädt die Variablen aus der Datei und weist sie globalen Variablen zu."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Lädt alle Einträge aus dem Dictionary direkt als globale Variablen
            globals().update(data)
            print(f"Konfiguration aus '{CONFIG_FILE}' erfolgreich geladen.")
    except FileNotFoundError:
        print(f"Datei '{CONFIG_FILE}' nicht gefunden. Erstelle Default-Konfiguration...")
        save_config()


# --- Beispiel für die Nutzung ---
if __name__ == "__main__":
    # 1. Konfiguration laden (überschreibt die globalen Variablen mit den Werten aus der Datei)
    load_config()

    # 2. Direkt auf die globalen Variablen zugreifen (ohne Dictionary-Syntax)
    print(f"frame_time = {frame_time}")
    print(f"blink_time = {blink_time}")

    # 3. Globale Variablen im Code verändern
    frame_time = 20

    # 4. Geänderte Werte speichern
    save_config()

