# Beispielklasse
class Objekt:
    def __init__(self, index, stripe, num_led):
        self.index      = index
        self.stripe     = stripe
        self.num_led    = num_led
        self.start_led  = 0
        self.stop_led   = 0
        self.color_off  = (0,0,0)
        

# Funktion, um alle Objekte mit einer bestimmten Eigenschaft zu finden
def finde_objekte_mit_eigenschaft(objekte, eigenschaft_wert):
    return [obj for obj in objekte if obj.stripe == eigenschaft_wert]

# Beispielobjekte
objekte = [
    Objekt(1,1,4),
    Objekt(2,1,6),
    Objekt(3,1,8),
    Objekt(4,2,8)
]

# Objekte mit Eigenschaft '1' finden
ergebnis = finde_objekte_mit_eigenschaft(objekte, 1)
for obj in ergebnis:
    print(obj.index, obj.stripe)

# Alle verschiedenen Eigenschaften ermitteln
eigenschaften = set(obj.stripe for obj in objekte)
print(eigenschaften)
eigenschaften_liste = sorted(eigenschaften)
print(eigenschaften_liste)

for value in eigenschaften_liste:
    print(value)

