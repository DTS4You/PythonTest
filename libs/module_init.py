# #############################################################################
# ### MyGlobal
# ### Bereich Raumfahrt V1.00
# #############################################################################

class Global_Module:
    
    inc_ws2812          = False
    inc_decoder         = False
    inc_serial          = False
    inc_i2c             = False

#------------------------------------------------------------------------------

class Global_Default:

    blink_freq          = 3.0           # Blink Frequenz

#==============================================================================

def three_d_array(value, *dim):
    """
    Create 3D-array
    :param dim: a tuple of dimensions - (x, y, z)
    :param value: value with which 3D-array is to be filled
    :return: 3D-array
    """
    # [Z][Y][0]   -> Stripe PIN Value
    # [Z][Y][1]   -> Start Position Start from 0
    # [Z][Y][2]   -> Number of LED in this Segment

    return [[[value for _ in range(dim[0])] for _ in range(dim[1])] for _ in range(dim[2])]

#------------------------------------------------------------------------------
def set_stripe_value(array):

    array[0][0][0] = 1      # 1. Stripe PIN
    array[0][0][2] = 3      # 1. Stripe ; 1. Segment  -> Teil 1.1
    array[0][1][2] = 6      # 1. Stripe ; 2. Segment  -> Teil 1.2
    array[0][2][2] = 9      # 1. Stripe ; 3. Segment  -> Teil 1.3
    array[0][3][2] = 9      # 1. Stripe ; 4. Segment  -> Teil 1.4

    array[1][0][0] = 2      # 2. Stripe PIN
    array[1][0][2] = 8      # 2. Stripe ; 1. Segment  -> Teil 2.1 
    array[1][1][2] = 8      # 2. Stripe ; 2. Segment  -> Teil 2.2 
    array[1][2][2] = 8      # 2. Stripe ; 3. Segment  -> Teil 2.3 
    array[1][3][2] = 8      # 2. Stripe ; 4. Segment  -> Teil 2.4 

    array[2][0][0] = 3      # 2. Stripe PIN
    array[2][0][2] = 4      # 3. Stripe ; 1. Segment  -> Teil 3.1 
    array[2][1][2] = 4      # 3. Stripe ; 2. Segment  -> Teil 3.2 
    array[2][2][2] = 0      # 3. Stripe ; 3. Segment  -> Teil 3.3 
    array[2][3][2] = 0      # 3. Stripe ; 4. Segment  -> Teil 3.4 

#------------------------------------------------------------------------------

def make_stripe_array(array):
    num_segment = len(array[0])
    num_stripes = len(array)
    #print(num_segment)
    #print(num_stripes)
    for z in range(num_stripes):
        for y in range(num_segment):
            if array[z][y][2] > 0 :     # Anzahl Pixel > 0
                if y > 0:               # Ab dem 2. Segment wird der Startwert berechnet
                    array[z][y][1] = array[z][y - 1][2] + array[z][y - 1][1]
                    array[z][y][0] = array[z][0][0]     # Stripe PIN set to first item

#------------------------------------------------------------------------------

class Global_WS2812:

    def __init__(self):

        self.numpix_1           = 16            # Anz. LEDs im 1. Stripe -> Boden 1
        self.numpix_2           = 16            # Anz. LEDs im 2. Stripe -> Boden 2
        self.numpix_3           = 16            # Anz. LEDs im 3. Stripe -> Boden 3
        self.numpix_4           = 16            # Anz. LEDs im 4. Stripe -> Boden 4
        self.numpix_5           = 16            # Anz. LEDs im 5. Stripe -> Boden 5
        self.numpix_6           = 320           # Anz. LEDs im 6. Stripe -> Spiegel, Laser, Empfänger
        self.numpix_7           = 256           # Anz. LEDs im 1. Stripe -> Test !!!
        self.default_value      = 0
        self.num_values         = 3
        self.num_segments       = 4
        self.num_stripes        = 3
        self.array              = []
    #--------------------------------------------------------------------------
    def three_d_array(self):

        # [Z][Y][0]   -> Stripe PIN Value
        # [Z][Y][1]   -> Start Position Start from 0
        # [Z][Y][2]   -> Number of LED in this Segment

        self.array = [[[self.default_value for _ in range(self.num_values)] for _ in range(self.num_segments)] for _ in range(self.num_stripes)]

   

    
# -----------------------------------------------------------------------------

    color_def           = (  0,  0,  2)
    color_off           = (  0,  0,  0)
    color_on            = (255, 10, 10)
    color_dot           = (110,  2,  2)
    color_half          = (110,  2,  2)
    color_blink_on      = (255, 20, 20)
    color_blink_off     = (  0,  0,  5)

#==============================================================================

def main():

    print("Start Global Init")
    mg = Global_WS2812
    print(mg.numpix_1)
    print(mg.array[0][0][0])



#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#------------------------------------------------------------------------------