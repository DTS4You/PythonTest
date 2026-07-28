# Led-Segment Klasse
class Led_Array:
    def __init__(self, fcode, stripe, index):
        self.fcode      = fcode             # HTML-Funktions-Code
        self.stripe     = stripe            # LED_Stripe beginnt mit 1 (PIO-Sektion, Pin-Zuordnung)
        self.index      = index             # LED_Segment im Stripe beginnt mit 1
        

# Funktion, um alle Objekte mit einer bestimmten Eigenschaft zu finden
def finde_objekte_mit_eigenschaft(objekte, eigenschaft_wert):
    return [obj for obj in objekte if obj.fcode == eigenschaft_wert]

#==============================================================================
# Objekte anlegen   (UID, Stripe, Index, Anzahl, Richtung)
led_array = [
    Led_Array( 1, 4, 12),
    Led_Array( 2, 4, 11),
    Led_Array( 3, 4, 7),
    Led_Array( 4, 4, 3),
    Led_Array( 4, 4, 5),
    Led_Array( 5, 4, 2),
    Led_Array( 5, 4, 6), 
    Led_Array( 6, 4, 1),
    Led_Array( 6, 4, 4), 
    Led_Array( 7, 4, 8),
    Led_Array( 7, 4, 9),
    Led_Array( 8, 4, 10),
    Led_Array( 9, 6, 5),
    Led_Array(10, 5, 8),
    Led_Array(11, 5, 6),
    Led_Array(11, 6, 6),
    Led_Array(12, 7, 2),
    Led_Array(12, 7, 3),
    Led_Array(13, 7, 1),
    Led_Array(14, 5, 4),
    Led_Array(14, 6, 3),
    Led_Array(15, 5, 1),
    Led_Array(15, 5, 2),
    Led_Array(15, 5, 3),
    Led_Array(15, 5, 4),
    Led_Array(16, 1, 1),
    Led_Array(16, 2, 1),
    Led_Array(17, 5, 3),
    Led_Array(17, 6, 4),
    Led_Array(18, 3, 1),
    Led_Array(19, 5, 7),
    Led_Array(19, 6, 7),
    Led_Array(20, 6, 8)
]


#==============================================================================

# Objekte mit Eigenschaft 'X' finden
#ergebnis = finde_Led_Segment_mit_eigenschaft(objekte, 1)
#for obj in ergebnis:
#    print(obj.index, obj.stripe, obj.num_led, obj.start_led)


def do_this(value):

    segments = []

    segments = led_array

    # Alle verschiedenen Eigenschaften ermitteln
    eigenschaften = set(obj.fcode for obj in segments)
    eigenschaften_liste = sorted(eigenschaften)
    print(eigenschaften_liste)
    last_index = 0
    for value in eigenschaften_liste:
        ergebnis = finde_objekte_mit_eigenschaft(segments, value)

    print(len(segments))

def main():

    do_this("red")

    do_this("green")

    do_this("red")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

