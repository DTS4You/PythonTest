# Example showing use of HSV colors
import time
from libs.neopixel import Neopixel

color_off       = (  0,  0,  0)
color_red       = ( 80,  0,  0)
color_green     = (  0, 80,  0)
color_blue      = (  0,  0, 80)
color_yellow    = ( 50, 50,  0)
color_default   = (  0,  0,  2)


class LED_STRIP:
    def __init__(self, num_pix, pio_num, pin_num, color_start, color_stop, direction, transfer_mode="PUT"):
        self.num_pix        = num_pix 
        self.pio_num        = pio_num 
        self.pin_num        = pin_num
        self.transfer       = transfer_mode
        self.color_default  = ( 0, 0, 5)
        self.color_start    = color_start
        self.color_stop     = color_stop
        self.color_value    = ( 40, 40, 40)
        self.anim_count     = 0
        self.anim_enable    = True
        self.anim_type      = "Pixel"
        self.direction      = direction

        self.led_setup()

    def led_setup(self):
        self.strip = (Neopixel(self.num_pix, self.pio_num, self.pin_num, "GRB", 0.0001, self.transfer))

    def led_set_pixel(self):
        self.strip.set_pixel(self.anim_count, self.color_value)

    def led_fill(self):
        self.strip.fill(self.color_default)

    def led_gradient(self):
        self.strip.set_pixel_line_gradient(0 ,self.num_pix - 1, self.color_start, self.color_stop)

    def led_show(self):
        self.strip.show()

    def mask_stripe(self):
        self.led_gradient()
        if self.anim_count > 0:
            self.strip.set_pixel_line(0, self.anim_count - 1 , color_default)
        if self.anim_count < self.num_pix - 2:
            self.strip.set_pixel_line(self.anim_count + 3, self.num_pix, color_default)
    
    def anim_step(self):
        print("Alt -> " + str(self.anim_count))
        if self.anim_enable:
            if self.direction:
                if self.anim_count < self.num_pix - 1:
                    self.anim_count += 1
                else:
                    self.anim_count = 0
            else:
                if self.anim_count > 0:
                    self.anim_count -= 1
                else:
                    self.anim_count = self.num_pix - 1
        #print("Neu -> " + str(self.anim_count))
    
    def make_anim(self):
        if self.anim_type == "Pixel":
            self.led_fill()
            self.led_set_pixel()
        self.anim_step()



led_1 = LED_STRIP(20, 0, 2, color_red, color_yellow, True)


#led_1.strip_fill()
led_1.led_gradient()
led_1.led_show()

time.sleep(2)

while(True):
    led_1.make_anim()
    led_1.led_show()
    time.sleep(0.1)


