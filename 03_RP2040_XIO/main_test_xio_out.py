from machine import Pin
from time import sleep

class XIO(object):
    def __init__(self, direction=False):
        self.direction = direction
        self.value = [False, False, False, False]
        self.init_setup()
        
    def init_setup(self):
        if self.direction == True:
            self.init_input()
        else:
            self.init_output()

    def init_input(self):
        self.io = [Pin(10, Pin.IN), Pin(11, Pin.IN), Pin(12, Pin.IN), Pin(13, Pin.IN)]
        self.io[0].value(False)
        self.io[1].value(False)
        self.io[2].value(False)
        self.io[3].value(False)

    def init_output(self):
        self.io = [Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]
        self.io[0].value(False)
        self.io[1].value(False)
        self.io[2].value(False)
        self.io[3].value(False)

def main():

    print("=== Start Main -> Module_XIO als Input ===")

    try:
        print("Start")
        xio = XIO(False)  # True for input, False for output

        while(True):
            xio.value[0] = True
            xio.value[1] = False
            xio.value[2] = True
            xio.value[3] = False
            sleep(0.5)
            xio.value[0] = False
            xio.value[1] = True
            xio.value[2] = False
            xio.value[3] = True
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
