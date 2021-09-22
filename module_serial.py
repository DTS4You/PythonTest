# Module Serial
import machine

debug = False

def serial_init():

    global uart
    
    uart = machine.UART(0)


def serial_write():

    uart.write("Hello22\n")


def mod_serial():
    
    serial_init()

    serial_write()
    

def main():
    mod_serial()



#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
