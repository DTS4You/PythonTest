# Module Serial
import machine

debug = False

def main():
    if debug:
        print("Test")

    uart = machine.UART(0)
    if debug:
        print(uart)

    uart.write("Hello\n")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
