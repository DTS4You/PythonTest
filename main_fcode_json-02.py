###############################################################################
### Programm    : Funktions-Codes in Array umwandeln
###############################################################################
import json
import os

class OBJECT:
    def __init__(self, name, array):
        self.name = name
        self.array = array

#==============================================================================
# Standarddaten, die geschrieben werden, falls die Datei fehlt oder leer ist
DEFAULT_DATA = [
    {"name": "H2Sat",       "array": [1, 2]},
    {"name": "EnMap",       "array": [3, 4]},
    {"name": "SARah",       "array": [11, 12, 15]},
    {"name": "SAR_Lupe",    "array": [3, 4]},
    {"name": "SATCOMBw",    "array": [1, 2, 5, 6, 7, 8]},
    {"name": "TerraSAR-X",  "array": [13, 14]},
    {"name": "SPOCK",       "array": None},
    {"name": "Galileo",     "array": [2, 3, 9, 10]},
    {"name": "Dummy_1",     "array": 45}
]
#==============================================================================

def load_or_create_json(filepath):
    # 1. Prüfen, ob die Datei existiert und nicht leer ist (Größe > 0 Bytes)
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(f"Datei '{filepath}' fehlt oder ist leer. Erstellig mit Standarddaten...")
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(DEFAULT_DATA, file, indent=4)

    # 2. Datei einlesen (mit try-except zur zusätzlichen Sicherheit)
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        print(f"Datei {filepath} geladen")
    except json.JSONDecodeError:
        print(f"Warnung: '{filepath}' enthielt ungültiges JSON. Fahre mit Standarddaten fort.")
        data = DEFAULT_DATA

    # 3. JSON-Daten in OBJECT-Instanzen umwandeln
    return [OBJECT(item["name"], item["array"]) for item in data]


def get_list_from_array(object_value):
    if isinstance(object_value, list):
        return object_value
    if isinstance(object_value, tuple):
        return list(object_value)
    if isinstance(object_value, int):
        return [object_value]
    return []


# --- Hauptprogramm ---
filepath = "cfg_fcode_array.json"

obj_array = load_or_create_json(filepath)

for obj in obj_array:
    print(f"{obj.name}: Länge: {len(get_list_from_array(obj.array))} -> {get_list_from_array(obj.array)}")

