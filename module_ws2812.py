import time
import module_neopixel

class LedState:
    def __init__(self):
        self.state = False

    def set(self, set):
        self.state = set

    def get(self):
        return self.state

    def refresh(self):
        self.state = False
        strip_1.show()

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

    global strip_1
    global led_1, led_2
    global ledstate
    
    ledstate = LedState()

    numpix = 16
    strip_1 = module_neopixel.Neopixel(numpix, 0, 2, "GRB")

    led_1 = Ledsegment(strip_1, 0, 2)
    led_2 = Ledsegment(strip_1, 2, 1)
    led_3 = Ledsegment(strip_1, 3, 1)
    led_4 = Ledsegment(strip_1, 4, 1)

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
    color_default = (0,0,20)
    colors_rgb = (red, white, red, green, blue, indigo, violet)

    # same colors as normaln rgb, just 0 added at the end
    colors_rgbw = [color+tuple([0]) for color in colors_rgb]
    colors_rgbw.append((0, 0, 0, 255))

    # uncomment colors_rgb if you have RGB strip
    colors = colors_rgb
    #colors = colors_rgbw

    strip_1.brightness(255)
   
    strip_1.set_pixel_line(0, 10, color_default)
    strip_1.show()

    led_1.set_color_off(black)
    led_1.set_default(red)
    led_1.set_color_on(white)

    led_2.set_color_off(black)
    led_2.set_default(red)
    led_2.set_color_on(green)


def do_test_on():
    print("Test on")
    #led_1.show_on()
    #led_2.show_on()
    #ledstate.set(True)

 
def do_test_off():
    print("Test off")
    #led_1.show_off()
    #led_2.show_off()
    #ledstate.set(True)

def do_refresh():
    ledstate.refresh()

def do_get_state():
    return ledstate.get()

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
