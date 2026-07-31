###############################################################################
### F_Code zu LED(s)
### V 1.00
###############################################################################
from machine import Pin

class HWDEBUG:
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

    pass    

#------------------------------------------------------------------------------
# Main-Funktion
#------------------------------------------------------------------------------
def main():

    hwdebug = HWDEBUG()

    hwdebug.write_output(1)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#--- Programmstart als Main-Programm
#------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#------------------------------------------------------------------------------