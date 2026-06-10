# Led-Segment Klasse
class Led_Segment:
    def __init__(self, uid, stripe_nr, index, num_led, direction=False):
        self.uid = uid  # LED_Segment UID fortlaufend ab 1
        self.stripe = stripe_nr  # LED_Stripe beginnt mit 1 (PIO-Sektion, Pin-Zuordnung)
        self.index = index  # LED_Segment im Stripe beginnt mit 1
        self.num_led = num_led  # Anzahl der LEDs im Segment
        self.start_led = 0  # Start-Position beginnt mit 0
        self.stop_led = 0  # Stop-Position beginnt mit 0
        self.direction = direction  # Richtung: False → Von links nach rechts | True → Von rechts nach links
        self.color_off = (0, 0, 0)
        self.refresh = False  # Wurde das Led_Segment verändert


# Funktion, um alle Objekte mit einer bestimmten Eigenschaft zu finden
def finde_objekte_mit_eigenschaft(objekte, eigenschaft_wert):
    return [obj for obj in objekte if obj.stripe == eigenschaft_wert]

stripe = []
# ==============================================================================
# Objekte anlegen   (UID, Stripe, Index, Anzahl, Richtung)
stripe_cfg_1 = [
    Led_Segment(1, 1, 1, 4, False),  # 1. Segment
    Led_Segment(2, 1, 2, 6, False),  # 2. Segment
    Led_Segment(3, 1, 3, 8, False),  # 3. Segment
    Led_Segment(4, 2, 1, 8, False),  # 4. Segment
    Led_Segment(5, 2, 2, 8, False),  # 5. Segment
    Led_Segment(6, 3, 1, 8, False),  # 6. Segment
    Led_Segment(7, 7, 1, 8, False)   # 7. Segment
]

stripe_cfg_2 = [
    Led_Segment(1, 1, 1, 4, True),   # 1. Segment
    Led_Segment(2, 1, 2, 6, False),  # 2. Segment
    Led_Segment(3, 1, 3, 8, True),   # 3. Segment
    Led_Segment(4, 2, 1, 8, False),  # 4. Segment
    Led_Segment(5, 2, 2, 8, True),   # 5. Segment
    Led_Segment(6, 2, 3, 8, False)   # 6. Segment
]

# ==============================================================================

# Objekte mit Eigenschaft 'X' finden
# ergebnis = finde_Led_Segment_mit_eigenschaft(objekte, 1)
# for obj in ergebnis:
#    print(obj.index, obj.stripe, obj.num_led, obj.start_led)


def do_this(value):
    segments = []

    if value == "red":
        segments = stripe_cfg_1
    if value == "green":
        segments = stripe_cfg_2

    # Alle verschiedenen Eigenschaften ermitteln
    eigenschaften = set(obj.stripe for obj in segments)
    eigenschaften_liste = sorted(eigenschaften)
    print(eigenschaften_liste)

    for value in eigenschaften_liste:
        #print(f'Value: {value}')
        ergebnis = finde_objekte_mit_eigenschaft(segments, value)
        last_stop = 0
        for obj in ergebnis:
            #print(obj.stripe)
            if obj.index == 1:
                obj.start_led   = 0
                obj.stop_led    = -1 + obj.num_led
            else:
                obj.start_led   = 1 + last_stop
                obj.stop_led    = -1 + obj.start_led + obj.num_led
            last_stop = obj.stop_led
            print(f'UID: {obj.uid:2}, Stripe: {obj.stripe:2}, Index: {obj.index:2}, Start: {obj.start_led:3}, Stop: {obj.stop_led:3}, Num: {obj.num_led:3}, Dir: {obj.direction}')

    #print(len(segments))


def main():
    do_this("red")

    do_this("green")

# ------------------------------------------------------------------------------
# --- Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

