import json
import os


class COLOR_OBJ:
    def __init__(self, index, red, green, blue, brightness=1):
        self.index = index
        self.red = red
        self.green = green
        self.blue = blue
        self.dummy = 0
        self.brightness = brightness
        self.rgb32 = 0
        self.bytes_to_int32()

    def bytes_to_int32(self, little_endian=True):
        if little_endian:
            # LSB zuerst
            self.rgb32 = (
                self.red
                | (self.green << 8)
                | (self.blue << 16)
                | (self.dummy << 24)
            )
        else:
            # MSB zuerst
            self.rgb32 = (
                (self.dummy << 24)
                | (self.blue << 16)
                | (self.green << 8)
                | self.red
            )

        return self.rgb32


# Standarddaten mit den Schlüsseln r, g, b
DEFAULT_COLOR_DATA = [
    {"index":  0, "r":   0, "g":   0, "b":   0, "brightness": 1},
    {"index":  1, "r":   0, "g":   0, "b":   3, "brightness": 1},
    {"index":  2, "r": 100, "g": 100, "b": 100, "brightness": 1},
    {"index":  3, "r":  50, "g":  50, "b":  50, "brightness": 1},
    {"index":  4, "r":   0, "g": 200, "b":   0, "brightness": 1},
    {"index":  5, "r":   0, "g":  10, "b":   0, "brightness": 1},
    {"index":  6, "r":  10, "g":  10, "b":  10, "brightness": 1},
    {"index":  7, "r":  10, "g":  10, "b":  10, "brightness": 1},
    {"index":  8, "r":   0, "g":  20, "b":   0, "brightness": 1},
    {"index":  9, "r":   0, "g":  50, "b":   0, "brightness": 1},
    {"index": 10, "r":   0, "g": 150, "b":   0, "brightness": 1},
    {"index": 11, "r":   0, "g":   0, "b":  20, "brightness": 1},
    {"index": 12, "r":   0, "g":   0, "b":  50, "brightness": 1},
    {"index": 13, "r":   0, "g":   0, "b": 150, "brightness": 1},
    {"index": 14, "r":  20, "g":   0, "b":   0, "brightness": 1},
    {"index": 15, "r":  70, "g":   0, "b":   0, "brightness": 1},
]


def load_or_create_colors(filepath):
    # 1. Datei anlegen, falls sie fehlt oder 0 Bytes groß (leer) ist
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(
            f"Datei '{filepath}' fehlt oder ist leer. Erstelle mit Standarddaten..."
        )
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(DEFAULT_COLOR_DATA, file, indent=4)

    # 2. JSON einlesen (inklusive Fehlerabfang bei ungültigem JSON)
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(
            f"Warnung: '{filepath}' ist ungültig/beschädigt. Verwende Standarddaten."
        )
        data = DEFAULT_COLOR_DATA

    # 3. Liste mit COLOR_OBJ Objekten erzeugen
    color_index = []
    for item in data:
        # Hier werden r, g, b aus dem JSON den Argumenten red, green, blue übergeben
        obj = COLOR_OBJ(
            index=item["index"],
            red=item["r"],
            green=item["g"],
            blue=item["b"],
            brightness=item.get("brightness", 1),
        )
        color_index.append(obj)

    return color_index


def save_colors_to_json(filepath, color_index):
    data = [
        {
            "index": obj.index,
            "r": obj.red,
            "g": obj.green,
            "b": obj.blue,
            "brightness": obj.brightness
        }
        for obj in color_index
    ]
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def int32_to_4bytes(val, little_endian=True):
    b0 = val & 0xFF
    b1 = (val >> 8) & 0xFF
    b2 = (val >> 16) & 0xFF
    b3 = (val >> 24) & 0xFF

    if little_endian:
        return b0, b1, b2, b3  # LSB -> MSB
    else:
        return b3, b2, b1, b0  # MSB -> LSB


def main():
    print("--- Start ---")

    filepath = "cfg_colors.json"
    color_index = load_or_create_colors(filepath)

    print("\n--- Test COLOR_OBJ ---")
    for obj in color_index:
        print(
            f"Index: {obj.index}, R: {obj.red}, G: {obj.green}, B: {obj.blue}, Brightness: {obj.brightness}, RGB32: {hex(obj.rgb32)}"
        )

    print("\n--- Test int32_to_4bytes ---")
    for obj in color_index:
        b0, b1, b2, b3 = int32_to_4bytes(obj.rgb32, little_endian=True)
        print(
            f"Index: {obj.index}, RGB32: {hex(obj.rgb32)}, Bytes: [{b0}, {b1}, {b2}, {b3}]"
        )

    print("--- Ende ---")


if __name__ == "__main__":
    main()
