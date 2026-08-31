import json

class MicroPythonConfig:
    def __init__(self, json_daten):
        # 1. Normale Werte mit Fallback laden
        self.wlan_ssid = json_daten.get("wlan_ssid", "StandardSSID")
        self.intervall = json_daten.get("intervall", 5)
        
        # 2. RGB-Farben sicher als Tuple extrahieren
        self.color_0 = self._parse_rgb(json_daten.get("color_0"))
        self.color_1 = self._parse_rgb(json_daten.get("color_1"))
        self.color_2 = self._parse_rgb(json_daten.get("color_2"))

    def _parse_rgb(self, color_dict):
        """Hilfsfunktion: Erzeugt ein (r, g, b) Tuple mit Absicherung."""
        if not isinstance(color_dict, dict):
            return (0, 0, 0)  # Standard: Aus (Schwarz)
        
        r = color_dict.get("r", 0)
        g = color_dict.get("g", 0)
        b = color_dict.get("b", 0)
        
        return (r, g, b)




# Dateipfad zur JSON-Datei
dateipfad = "cfg.json"

try:
    # 1. Datei im Lesemodus ("r") öffnen
    with open(dateipfad, "r", encoding="utf-8") as datei:
        # 2. JSON-Inhalt parsen und in ein Python-Dictionary / eine Liste laden
        daten = json.load(datei)

    # 3. Mit den Daten arbeiten
    print("Erfolgreich geladen:")
    print(daten)

except FileNotFoundError:
    print(f"Fehler: Die Datei '{dateipfad}' wurde nicht gefunden.")
except json.JSONDecodeError:
    print(f"Fehler: Die Datei '{dateipfad}' enthält kein gültiges JSON-Format.")

cfg = MicroPythonConfig(daten)


print(cfg.color_0)
print(cfg.color_1)
print(cfg.color_2)
print(cfg.intervall)
