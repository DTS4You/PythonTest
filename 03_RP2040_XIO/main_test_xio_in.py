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

    print("=== Start Main -> Module_XIO als Input ===")

    try:
        print("Start")
        xio = XIO(True)  # True for input, False for output

        while(True):
            xio.io_read()
            print(xio.value[0], xio.value[1], xio.value[2], xio.value[3])
            sleep(0.3)

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
