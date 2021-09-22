# Main Program
import machine
import time
#from module_loader import mod_loader 
#import module_serial

led = machine.Pin(25, machine.Pin.OUT)


def main():
    delay_ms = 1000
    while True:
        led.toggle()
        time.sleep_ms(delay_ms)


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
