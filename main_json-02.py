import json

class Config:
    def __init__(self):
        # Definiere erlaubte Attribute mit Standardwerten (Fallbacks)
        self.hostname = "Unbekannt"
        self.intervall = 10
        self.status = False

    def lade_daten(self, json_daten):
        for key, value in json_daten.items():
            # Nur aktualisieren, wenn das Attribut auf der Klasse bereits existiert
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warnung: Unerwünschter Schlüssel '{key}' ignoriert.")

    def zeige_wert(self, attributname):
        # Sicheres Auslesen: Wenn ein Attribut fehlt, wird ein Default-Wert zurückgegeben
        return getattr(self, attributname, "Attribut nicht vorhanden")


# Test 1: JSON mit fehlenden Werten UND unerwünschten Schlüsseln
json_daten = {
    "hostname": "Pico-01",
    "unbekannter_schluessel": 999  # Wird ignoriert
    # "intervall" fehlt komplett -> behält Standardwert (10)
}

cfg = Config()
cfg.lade_daten(json_daten)

print(cfg.hostname)                # Output: Pico-01
print(cfg.intervall)               # Output: 10 (Fallback genutzt!)
print(cfg.zeige_wert("status"))    # Output: False
print(cfg.zeige_wert("akku_stand"))# Output: Attribut nicht vorhanden

