import json

class OBJECT:
    def __init__(self, name, array):
        self.name = name
        self.array = array

def load_objects_from_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    # Aus den JSON-Daten OBJECT-Instanzen erzeugen
    return [OBJECT(item["name"], item["array"]) for item in data]

def get_list_from_array(object_value):
    if isinstance(object_value, list):
        return object_value
    if isinstance(object_value, tuple):
        return list(object_value)
    if isinstance(object_value, int):
        return [object_value]
    return []

# Einlesen und Ausführen
obj_array = load_objects_from_json("funktionen.json")

for obj in obj_array:
    print(get_list_from_array(obj.array))
