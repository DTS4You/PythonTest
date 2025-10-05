#------------------------------------------------------------------------------
# Sound     : Play Tone
# Version   : 1.00
#------------------------------------------------------------------------------

from machine import Pin
from time import sleep

class XIO(object):
    def __init__(self, direction=False):
        self.direction = direction
        self.init_setup()
        
    def init_setup(self):
        if self.direction == True:
            self.init_input()
        else:
            self.init_output()

    def init_input(self):
        print("INPUT")
        self.value = [False, False, False, False]
        self.io = [Pin(10, Pin.IN), Pin(11, Pin.IN), Pin(12, Pin.IN), Pin(13, Pin.IN)]
        for i in range(4):
            self.value[i] = bool(self.io[i].value())
    
    def init_output(self):
        print("OUTPUT")
        self.value = [False, False, False, False]
        self.io = [Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]
        for i in range(4):
            self.io[i].value(False)

    def io_read(self):
        for i in range(4):
            self.value[i] = bool(self.io[i].value())

    def io_write(self):
        for i in range(4):
            self.io[i].value(self.value[i])

# -----------------------------------------------------------------------------
def main():

    print("=== Start Main -> Module_Sound ===")

    try:
        print("Start")
        xio = XIO(False)

        while(True):
            xio.value[0] = True
            xio.value[1] = False
            xio.value[2] = True
            xio.value[3] = False
            xio.io_write()
            sleep(0.5)
            xio.value[0] = False
            xio.value[1] = True
            xio.value[2] = False
            xio.value[3] = True
            xio.io_write()
            sleep(0.5)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        print("Exiting the program")
    print("=== End Main ===")

# ------------------------------------------------------------------------------
# --- Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# =============================================================================
