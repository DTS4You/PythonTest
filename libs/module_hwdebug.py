###############################################################################
### F_Code zu LED(s)
### V 1.00
###############################################################################
from machine import Pin

class hwdebug:
    def __init__(self):
        self.led_board      = Pin(25, Pin.OUT)
        self.switch_board   = Pin(24, Pin.IN, Pin.PULL_UP)
        self.switch_extern  = Pin(17, Pin.IN, Pin.PULL_UP)

    def read_input(self):
        return not (self.switch_board.value() and self.switch_extern.value())

    def write_output(self, value):
        self.led_board.value(value)

    
#==============================================================================
# Test-Funktion
def do_this(value):

    f_code_list = make_fcode_list()

    ergebnis = f_code_2_array(f_code_list, value)
    print("Anzahl:", len(ergebnis))
    for obj in ergebnis:
        print("Stripe:", obj.stripe, "Index:", obj.index)

#------------------------------------------------------------------------------
# Main-Funktion
#------------------------------------------------------------------------------
def main():

    do_this(1)
    do_this(17)

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#--- Programmstart als Main-Programm
#------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#------------------------------------------------------------------------------