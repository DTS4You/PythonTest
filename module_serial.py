# Module Serial
from machine import UART
import time

debug = False

class SERCON:

    def __init__(self):

        self.uart = UART(0, baudrate=115200, bits=8, parity=None, stop=1)

    def write(self, string):

        self.uart.write(string)

    def read(self):

        while self.uart.any() > 0:
            rxData = self.uart.readline()
            print("Input_S")
            print(rxData)
            print("Input_E")



def main():
    
    sercon = SERCON()

    txdata = b'hello world\n'
    sercon.write(txdata)

    time.sleep(5)

    print("Read")
    
    sercon.read()

    print("Ende")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
