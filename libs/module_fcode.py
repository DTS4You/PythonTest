###############################################################################
### F_Code zu LED(s)
### V 1.00
###############################################################################

class Led_Array:
    def __init__(self, fcode, stripe, index):
        self.fcode      = fcode             # HTML-Funktions-Code
        self.stripe     = stripe            # LED_Stripe beginnt mit 1 (PIO-Sektion, Pin-Zuordnung)
        self.index      = index             # LED_Segment im Stripe beginnt mit 1
        

#==============================================================================
# Objekte anlegen   (F-Code, Stripe, Index)
def make_fcode_list():
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
    return led_array


#==============================================================================

# Funktion, um alle Objekte mit einer bestimmten Eigenschaft zu finden
def f_code_2_array(objekte, eigenschaft_wert):
    return [obj for obj in objekte if obj.fcode == eigenschaft_wert]




def do_this(value):

    f_code_list = make_fcode_list()

    ergebnis = f_code_2_array(f_code_list, value)
    print(len(ergebnis))
    for obj in ergebnis:
        print(obj.stripe, obj.index)
    

def main():

    do_this(1)
    do_this(2)


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

