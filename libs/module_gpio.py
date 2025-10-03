# #############################################################################
# ### GPIO
# ### V 1.00
# #############################################################################
from machine import Pin, I2C # type: ignore
import libs.mcp23017_raw as mcp23017
import time # type: ignore

#i2c = I2C(0, scl=Pin(21), sda=Pin(20))
#mcp = mcp23017.MCP23017(i2c, 0x20)


class GPIO:

    def __init__(self):
        self.i2c = I2C(0, scl=Pin(21), sda=Pin(20))
        self.mcp = mcp23017.MCP23017(self.i2c, 0x20)
        self.inputs = 0x00
        self.outputs = 0x00

    def get_input(self):
        self.inputs = int.from_bytes(self.mcp._read(0x13, 1), 'big')

    def set_output(self):
        self.mcp._write([0x12, self.outputs])
        return self.outputs



# -----------------------------------------------------------------------------
def main():

    print("=== Start Main -> Module_Sound ===")

    try:
        print("Start")

        gpio = GPIO()

        while(True):

            
            print(bin(gpio.outputs))
    
            time.sleep(0.2)
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
