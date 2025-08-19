# Led-Segment Klasse
class Led_Segment:
    def __init__(self, uid, stripe, index, num_led, direction=False):
        self.index      = uid               # LED_Segment UID fortlaufend ab 1
        self.stripe     = stripe            # LED_Stripe beginnt mit 1 (PIO-Sektion, Pinzuordnung)
        self.index      = index             # LED_Segemnt im Stripe beginnt mit 1
        self.num_led    = num_led           # Anzahl der LEDs im Segment
        self.start_led  = 0                 # Startposition beginnt mit 0
        self.stop_led   = 0                 # Stopposition beginnt mit 0
        self.direction  = direction         # Richtung False -> Links nach Rechts / True -> Rechts nach links
        self.color_off  = (0,0,0)
        self.refresh    = False             # Wurde das Led_Segment verändert
        

# Funktion, um alle Objekte mit einer bestimmten Eigenschaft zu finden
def finde_objekte_mit_eigenschaft(objekte, eigenschaft_wert):
    return [obj for obj in objekte if obj.stripe == eigenschaft_wert]

# Objekte anlegen   (UID, Stripe, Index, Anzahl, Richtung)
segments = [
    Led_Segment(1, 1, 1, 4, False),        # 1. Segment
    Led_Segment(2, 1, 2, 6, True),         # 2. Segment
    Led_Segment(3, 1, 3, 8, False),        # 3. Segment
    Led_Segment(4, 2, 1, 8, True),         # 4. Segment
    Led_Segment(5, 2, 2, 8, False)         # 5. Segment
]

# Objekte mit Eigenschaft 'X' finden
#ergebnis = finde_Led_Segment_mit_eigenschaft(objekte, 1)
#for obj in ergebnis:
#    print(obj.index, obj.stripe, obj.num_led, obj.start_led)

# Alle verschiedenen Eigenschaften ermitteln
eigenschaften = set(obj.stripe for obj in segments)
eigenschaften_liste = sorted(eigenschaften)
last_index = 0
for value in eigenschaften_liste:
    ergebnis = finde_objekte_mit_eigenschaft(segments, value)
    for obj in ergebnis:
        if value is not last_index:
            last_index = obj.index
        else:
            segments[obj.index - 1].start_led = segments[obj.index - 2].num_led + segments[obj.index - 2].start_led
        segments[obj.index - 1].stop_led = segments[obj.index - 1].start_led + segments[obj.index - 1].num_led
        print(obj.index, obj.stripe, obj.start_led, obj.stop_led, obj.num_led, obj.direction)

    

