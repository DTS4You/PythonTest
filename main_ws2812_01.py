# Example showing use of HSV colors
import time
from libs.neopixel import Neopixel


class LED_STRIP:
    def __init__(self, num_pix, pio_num, pin_num, transfer_mode="PUT"):
        self.num_pix    = num_pix 
        self.pio_num    = pio_num 
        self.pin_num    = pin_num
        self.transfer   = transfer_mode

    def strip_setup(self):
        self.strip = (Neopixel(self.num_pix, self.pio_num, self.pin_num, "GRB", 0.0001, self.transfer))


led = []

led.append(LED_STRIP(20, 0, 2))




color_off       = (  0,  0,  0)
color_red       = ( 80,  0,  0)
color_green     = (  0, 80,  0)
color_blue      = (  0,  0, 80)
color_yellow    = ( 50, 50,  0)
color_default   = (  0,  0,  2)


led[0].strip_setup()

led[0].strip.set_pixel_line(0, 19, color_red)
led[0].strip.show()

