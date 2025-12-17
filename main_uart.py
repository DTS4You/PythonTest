######################################################
### Main-Program                                   ###
### Projekt: Python Test                           ###
### Version: 0.99                                  ###
### Datum  : 11.08.2025                            ###
######################################################

from machine import UART
import time

uart = UART(0, baudrate=9600, bits=8, parity=None, stop=1)                        # type: ignore    # init with given baudrate

uart.deinit() # type: ignore

uart = UART(0, baudrate=9600, bits=8, parity=None, stop=1)                        # type: ignore


string = "Test\n"

uart.write(str.encode(string))

while True:
    rxdata = uart.readline()
    uart.write(str.encode(string))
    #print("Tx-Done", uart.txdone())
    print(str(rxdata) + " -> " + str(uart.any()))
    print("Wait")
    time.sleep(0.5)
