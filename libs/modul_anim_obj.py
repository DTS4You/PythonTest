import json
import os
import time


class ANIM_PATTERN:
    def __init__(self, led_pattern):
        self.led_pattern = led_pattern
        self.length = len(self.led_pattern)


class ANIM_OBJ:
    def __init__(self, stripe, start, length, pattern, default_color_index=0, direction=True):
        self.stripe         = stripe                        # Stripe Nummmer zählt von 1 bis N -> muss zum Board mit 0 starten
        self.start          = start                         # Startposition im Stripe Start bei 1
        self.led_length     = length
        self.color_def      = default_color_index
        self.pattern        = pattern
        self.position       = 0
        self.direction      = direction                     # True = rechts -> links / False = links -> rechts
        self.modulo         = 0
        self.modified       = False

        self.led_array = self.pattern.led_pattern + [
            self.color_def
        ] * self.led_length
        self.arr_length = self.led_length + self.pattern.length
        self.act_array = self.led_array

    def get_modulo(self):
        self.modulo = self.position % len(self.led_array)
        return self.modulo

    def get_led_array(self):
        return self.led_array

    def do_anim_step(self):
        arr_len = len(self.led_array)
        n = self.position % arr_len

        # Rotation ausführen
        if self.direction:
            # Rechts-Rotation
            self.act_array = self.led_array[-n:] + self.led_array[:-n]
        else:
            # Links-Rotation
            self.act_array = self.led_array[n:] + self.led_array[:n]

        # Position hochzählen/zurücksetzen
        if self.position >= self.arr_length:
            self.position = 0
        else:
            self.position += 1

        return self.act_array[self.pattern.length :]


# Standarddaten
DEFAULT_PATTERNS = [
    [8, 9, 10, 9, 8],  # Index 0 (Grün)
    [14, 15, 14],  # Index 1 (Rot)
    [11, 12, 13, 12, 11],  # Index 2 (Blau)
]

DEFAULT_OBJECTS = [
    {"stripe":  1, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  2, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  3, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  4, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  5, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  6, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  7, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  8, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  9, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 10, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 11, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 11, "start": 20, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 12, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 12, "start": 20, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 13, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 14, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 15, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
]


def load_or_create_patterns(filepath):
    """Lädt Patterns aus JSON oder erstellt Standarddatei."""
    is_empty_or_missing = True
    try:
        if os.stat(filepath)[6] > 0:
            is_empty_or_missing = False
    except OSError:
        is_empty_or_missing = True

    if is_empty_or_missing:
        print(
            f"Datei '{filepath}' fehlt/leer. Erstelle mit Standarddaten..."
        )
        with open(filepath, "w") as file:
            json.dump(DEFAULT_PATTERNS, file)

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except (ValueError, OSError):
        print(f"Warnung: '{filepath}' ungültig. Verwende Standarddaten.")
        data = DEFAULT_PATTERNS

    return [ANIM_PATTERN(pat) for pat in data]


def save_objects_to_json(filepath, objects_data):
    """Speichert Objekte in einzeiliger Form ab."""
    lines = ["["]
    count = len(objects_data)
    for i, item in enumerate(objects_data):
        comma = "," if i < count - 1 else ""
        lines.append(
            f'    {{ "stripe": {item["stripe"]:2d}, "start": {item["start"]:2d}, "length": {item["length"]:2d}, "pattern_index": {item["pattern_index"]}, "default_color_index": {item["default_color_index"]}, "direction": {str(item["direction"]).lower()} }}{comma}'
        )
    lines.append("]")

    with open(filepath, "w") as file:
        file.write("\n".join(lines))


def load_or_create_objects(filepath, anim_patterns):
    """Lädt Objekt-Konfigurationen aus JSON oder erstellt Standarddatei."""
    is_empty_or_missing = True
    try:
        if os.stat(filepath)[6] > 0:
            is_empty_or_missing = False
    except OSError:
        is_empty_or_missing = True

    if is_empty_or_missing:
        print(
            f"Datei '{filepath}' fehlt/leer. Erstelle mit Standarddaten..."
        )
        save_objects_to_json(filepath, DEFAULT_OBJECTS)

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except (ValueError, OSError):
        print(f"Warnung: '{filepath}' ungültig. Verwende Standarddaten.")
        data = DEFAULT_OBJECTS

    anim_objects = []
    for item in data:
        pat_idx = item["pattern_index"]
        obj = ANIM_OBJ(
            stripe=item["stripe"],
            start=item["start"],
            length=item["length"],
            pattern=anim_patterns[pat_idx],
            default_color_index=item["default_color_index"],
            direction=item["direction"]
        )
        anim_objects.append(obj)

    return anim_objects


def main():
    print("--- Start ---")

    patterns_file = "cfg_patterns.json"
    objects_file = "cfg_anim_objects.json"

    anim_pattern = load_or_create_patterns(patterns_file)
    anim_obj = load_or_create_objects(objects_file, anim_pattern)

    print("Objekte erzeugt")

    if len(anim_obj) > 1:
        anim_obj[1].modified = True

    print("Anzahl der Patterns:", len(anim_pattern))
    print("Anzahl der Anim_Objekte:", len(anim_obj))

    if anim_obj:
        print("Pattern 0 Länge:", anim_obj[0].pattern.length)
        print("Array Länge Gesamt:", anim_obj[0].arr_length)

        for _ in range(20):
            print(
                f"Objekt Pos: {anim_obj[0].position:02d} | Array: {anim_obj[0].do_anim_step()}"
            )
            time.sleep(0.2)

    print("--- Ende ---")

#==============================================================================
if __name__ == "__main__":
    main()
#==============================================================================