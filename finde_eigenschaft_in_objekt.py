# Beispielklasse
class Objekt:
    def __init__(self, index, stripe, num_led, direction=False):
        self.index      = index
        self.stripe     = stripe
        self.num_led    = num_led
        self.start_led  = 0
        self.stop_led   = 0
        self.direction  = direction
        self.color_off  = (0,0,0)
        

# Funktion, um alle Objekte mit einer bestimmten Eigenschaft zu finden
def finde_objekte_mit_eigenschaft(objekte, eigenschaft_wert):
    return [obj for obj in objekte if obj.stripe == eigenschaft_wert]

# Beispielobjekte
objekte = [
    Objekt(1, 1, 4, False),
    Objekt(2, 1, 6,True),
    Objekt(3, 1, 8,False),
    Objekt(4, 2, 8,True),
    Objekt(5, 2, 8,False)
]

# Objekte mit Eigenschaft 'X' finden
#ergebnis = finde_objekte_mit_eigenschaft(objekte, 1)
#for obj in ergebnis:
#    print(obj.index, obj.stripe, obj.num_led, obj.start_led)

# Alle verschiedenen Eigenschaften ermitteln
eigenschaften = set(obj.stripe for obj in objekte)
eigenschaften_liste = sorted(eigenschaften)
last_index = 0
for value in eigenschaften_liste:
    ergebnis = finde_objekte_mit_eigenschaft(objekte, value)
    for obj in ergebnis:
        if value is not last_index:
            last_index = obj.index
        else:
            objekte[obj.index - 1].start_led = objekte[obj.index - 2].num_led + objekte[obj.index - 2].start_led
        objekte[obj.index - 1].stop_led = objekte[obj.index - 1].start_led + objekte[obj.index - 1].num_led
        print(obj.index, obj.stripe, obj.start_led, obj.stop_led, obj.num_led, obj.direction)

    

