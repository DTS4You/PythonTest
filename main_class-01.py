class Person:
    def __init__(self, alter):
        # Ruft direkt den Setter auf, um auch beim Erstellen zu prüfen
        self.alter = alter

    # 1. Der Getter (macht das Attribut lesbar)
    @property
    def alter(self):
        return self._alter

    # 2. Der SETTER (wird automatisch aufgerufen bei: p.alter = wert)
    @alter.setter
    def alter(self, neuer_wert):
        if neuer_wert < 0:
            raise ValueError("Das Alter kann nicht negativ sein!")
        if not isinstance(neuer_wert, int):
            raise TypeError("Das Alter muss eine Ganzzahl sein!")
        
        # Erst wenn alle Prüfungen bestanden sind, wird der Wert gespeichert:
        self._alter = neuer_wert


# --- Anwendung ---
p = Person(25)

# Funktionsweise beim Ändern:
p.alter = 30  # ✅ Funktioniert sauber (Setzt self._alter auf 30)

print(p.alter)

try:
    p.alter = -5  # ❌ Bricht ab mit ValueError: "Das Alter kann nicht negativ sein!"
except ValueError as e:
    print(f"Abgefangen: {e}")

