# Module Serial
from machine import UART
import time

debug = False

class SERCON:

    def __init__(self):

        self.uart = UART(0, baudrate=115200, bits=8, parity=None, stop=1)
        self.line = ""
        self.flag = True

    def write(self, string):

        self.uart.write(string)

    def read(self):
        self.line = self.uart.readline()
        if self.line:
            self.flag = True
            return self.line
        else:
            self.flag = False
            time.sleep(0.01)
            return False
        


def main():
    
    sercon = SERCON()

    txdata = b'hello world\n'
    sercon.write(txdata)

    time.sleep(1)

    print("Read")
    
    while True:
        if sercon.read():
            print(sercon.line)
            sercon.write("ack\n")
        
    
        

    print("Ende")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
