import json
import os
import time


class ANIM_PATTERN:
    def __init__(self, led_pattern):
        self.led_pattern = led_pattern
        self.lenght = len(self.led_pattern)


class ANIM_OBJ:
    def __init__(self, stripe, start, lenght, pattern, default_color_index=0, direction=True):
        self.stripe = stripe
        self.start = start
        self.led_lenght = lenght
        self.color_def = default_color_index
        self.pattern = pattern
        self.position = 0
        self.direction = (
            direction  # True = rechts -> links / False = links -> rechts
        )
        self.modulo = 0
        self.modifyed = False
        self.led_array = self.pattern.led_pattern + [
            self.color_def
        ] * self.led_lenght
        self.arr_lenght = self.led_lenght + self.pattern.lenght
        self.act_array = self.led_array

    def get_modulo(self):
        self.modulo = self.position % len(self.led_array)

    def get_led_array(self):
        return self.led_array

    def rotate_right(self, n):
        n = n % len(self.led_array)
        return self.led_array[-n:] + self.led_array[:-n]

    def rotate_left(self, n):
        n = n % len(self.led_array)
        return self.led_array[n:] + self.led_array[:n]

    def do_anim_step(self):
        if self.direction:
            self.act_array = self.rotate_right(self.position)
        else:
            self.act_array = self.rotate_left(self.position)

        if self.position >= self.arr_lenght:
            self.position = 0
        else:
            self.position = self.position + 1

        return self.act_array[self.pattern.lenght :]


# Standarddaten getrennt definieren
DEFAULT_PATTERNS = [
    [8, 9, 10, 9, 8],           # Index 0 (Grün)
    [14, 15, 14],               # Index 1 (Rot)
    [11, 12, 13, 12, 11],       # Index 2 (Blau)
]

DEFAULT_OBJECTS = [
    {"stripe":  1, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  2, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  3, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  4, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  5, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  6, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  7, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  8, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  9, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 10, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 11, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 11, "start": 20, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 12, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 12, "start": 20, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 13, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 14, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 15, "start":  1, "lenght": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
]


def load_or_create_patterns(filepath):
    """Lädt die Patterns aus einer eigenen JSON-Datei oder erstellt sie."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(
            f"Datei '{filepath}' fehlt oder ist leer. Erstelle mit Standarddaten..."
        )
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(DEFAULT_PATTERNS, file, indent=4)

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(
            f"Warnung: '{filepath}' ist ungültig. Verwende Standarddaten."
        )
        data = DEFAULT_PATTERNS

    return [ANIM_PATTERN(pat) for pat in data]


def load_or_create_objects(filepath, anim_patterns):
    """Lädt die Objekt-Konfigurationen aus einer eigenen JSON-Datei oder erstellt sie."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(
            f"Datei '{filepath}' fehlt oder ist leer. Erstelle mit Standarddaten..."
        )
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(DEFAULT_OBJECTS, file, indent=4)

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(
            f"Warnung: '{filepath}' ist ungültig. Verwende Standarddaten."
        )
        data = DEFAULT_OBJECTS

    anim_objects = []
    for item in data:
        pat_idx = item["pattern_index"]
        obj = ANIM_OBJ(
            stripe=item["stripe"],
            start=item["start"],
            lenght=item["lenght"],
            pattern=anim_patterns[pat_idx],
            default_color_index=item.get("default_color_index", 0),
            direction=item.get("direction", True),
        )
        anim_objects.append(obj)

    return anim_objects


def main():
    print("--- Start ---")

    patterns_file   = "cfg_patterns.json"
    objects_file    = "cfg_anim_objects.json"

    # 1. Zuerst Patterns laden
    anim_pattern = load_or_create_patterns(patterns_file)

    # 2. Dann Animationsobjekte laden und mit den loaded Patterns verknüpfen
    anim_obj = load_or_create_objects(objects_file, anim_pattern)

    print("Objekte erzeugt")

    if len(anim_obj) > 1:
        anim_obj[1].modifyed = True

    print("Anzahl der Patterns:", len(anim_pattern))
    print("Anzahl der Anim_Objekte:", len(anim_obj))

    if anim_obj:
        print("Pattern 0 Länge:", anim_obj[0].pattern.lenght)
        print("Array Länge Gesamt:", anim_obj[0].arr_lenght)

        for i in range(20):
            print(
                f"Objekt: {anim_obj[0].position:02d} Array: {anim_obj[0].do_anim_step()}"
            )
            time.sleep(0.2)

    print("--- Ende ---")


# ------------------------------------------------------------------------------
# --- Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()