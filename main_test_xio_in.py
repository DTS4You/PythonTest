from machine import Pin
from time import sleep

class XIO(object):
    def __init__(self, direction="OUTPUT"):
        self.direction = direction
        self.value = [False, False, False, False]
        self.init_setup()
        
    def init_setup(self):
        if self.direction == "OUTPUT":
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

xio = XIO("OUTPUT")

xio.io[0].value(True)
xio.io[2].value(True)

print(xio.value[0])

