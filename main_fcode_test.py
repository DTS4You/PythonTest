###############################################################################
### F_Code zu LED(s)
### V 1.00
###############################################################################

import libs.module_fcode as fcode


def fcode_function(value):

    fcode_array = fcode.make_fcode_list()
    fcode_led = fcode.f_code_2_array(fcode_array, value)
    return fcode_led

def main():

    fcode = 2
    fcode_led = fcode_function(fcode)
    print(len(fcode_led))
    for led in fcode_led:
        print(led.stripe, led.index)

#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
