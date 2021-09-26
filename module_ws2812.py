import time
from neopixel import Neopixel


class Ledsegment:

    def __init__(self, neopixel, start, count):
        self.neopixel = neopixel
        self.start = start
        self.stop = self.start + count - 1
        self.count = count
        self.color_on = (0,0,0)
        self.color_default = (0,0,0)
        self.color_off = (0,0,0)
        self.color_show = (0,0,0)
    

    def set_color_on(self, color_on):
        self.color_on = color_on

    def set_default(self, color_default):
        self.color_default = color_default
        
    def set_color_off(self, color_off):
        self.color_off = color_off

    def show_on(self):
        self.color_show = self.color_on
        self.set_pixel()

    def show_def(self):
        self.color_show = self.color_default
        self.set_pixel()

    def show_off(self):
        self.color_show = self.color_off
        self.set_pixel()

    def set_pixel(self):
        self.neopixel.set_pixel_line(self.start, self.stop, self.color_show)

    def show_stripe(self):
        self.neopixel.show()


def setup_ws2812():

    global strip_1, strip_2
    global led_1, led_2

    numpix = 16
    strip_1 = Neopixel(numpix, 0, 2, "GRB")
    strip_2 = Neopixel(numpix, 1, 3, "GRB")

    led_1 = Ledsegment(strip_1, 0, 1)
    led_2 = Ledsegment(strip_1, 1, 1)

    red = (255, 0, 0)
    orange = (255, 165, 0)
    yellow = (255, 150, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    indigo = (75, 0, 130)
    violet = (138, 43, 226)
    white = (255,255,255)
    grey = (50,50,50)
    black = (0,0,0)
    colors_rgb = (red, white, red, green, blue, indigo, violet)

    # same colors as normaln rgb, just 0 added at the end
    colors_rgbw = [color+tuple([0]) for color in colors_rgb]
    colors_rgbw.append((0, 0, 0, 255))

    # uncomment colors_rgb if you have RGB strip
    colors = colors_rgb
    #colors = colors_rgbw

    strip_1.brightness(20)
    strip_2.brightness(50)

    strip_2.set_pixel_line_gradient(0, 7, white, grey)
    strip_2.set_pixel_line_gradient(8, 15, grey, white)

    strip_1.set_pixel_line(0, 10, orange)
    strip_1.show()
    strip_2.show()

    led_1.set_color_off(black)
    led_1.set_default(red)
    led_1.set_color_on(white)

    led_2.set_color_off(black)
    led_2.set_default(red)
    led_2.set_color_on(green)

def do_test_on():
        led_1.show_on()
        led_2.show_on()
        strip_1.show()
 
def do_test_off():
        led_1.show_off()
        led_2.show_off()
        strip_1.show()

def run_ws2812():

    while True:
        led_1.show_on()
        led_2.show_on()
        strip_1.show()
        time.sleep(0.3)
        led_1.show_off()
        led_2.show_off()
        strip_1.show()
        time.sleep(0.3)

def main():

    setup_ws2812()
    run_ws2812()


# End

#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
