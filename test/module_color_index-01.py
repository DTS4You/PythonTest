###############################################################################
### Module: module_anim_obj.py
###############################################################################
import time

def color_setup():

    global color_index
    color_index = []

    color_index.append(COLOR_OBJ( 0,  0,  0,  0))
    color_index.append(COLOR_OBJ( 1, 10, 20, 30))


class COLOR_OBJ:
    def __init__(self, index, red, green, blue, brightness=1):
        self.index      = index
        self.red        = red
        self.green      = green
        self.blue       = blue
        self.dummy      = 0
        self.brightness = brightness
        self.rgb32      = 0
        self.bytes_to_int32()
    
    def bytes_to_int32(self, little_endian=True):
        if little_endian:
            # LSB zuerst
            self.rgb32 = self.red | (self.green << 8) | (self.blue << 16) | (self.dummy << 24)
        else:
            # MSB zuerst
            self.rgb32 = (self.dummy << 24) | (self.blue << 16) | (self.green << 8) | self.red

        return self.rgb32

 


def int32_to_4bytes(val, little_endian=True):
    
    b0 = val & 0xFF
    b1 = (val >> 8) & 0xFF
    b2 = (val >> 16) & 0xFF
    b3 = (val >> 24) & 0xFF

    if little_endian:
        return b0, b1, b2, b3  # LSB -> MSB
    else:
        return b3, b2, b1, b0  # MSB -> LSB



def main():

    print("--- Start ---")

    color_setup()

    value = color_index[1].rgb32
    print(value)


    # Beispiel:
    b0, b1, b2, b3 = int32_to_4bytes(value, little_endian=True)
    print(f"Bytes: {b0}, {b1}, {b2}, {b3}")  # Ausgabe: 1, 2, 3, 4


    print("--- Ende ---")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

