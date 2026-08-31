# Module WS2812 V1.01
import time # type: ignore
import libs.module_neopixel as module_neopixel
from libs.module_init import Global_WS2812 as MyGlobal


class LedState:
    def __init__(self):
        self.state = False
        self.blink_state = False

    def set(self, set):
        self.state = set

    def get(self):
        return self.state
    
    def do_blink(self):
        self.blink_state = not self.blink_state

    def get_blink(self):
        return self.blink_state

    def refresh(self):
        self.state = False
        for strips in strip_obj:
            strips.show()


class Ledsegment:

    def __init__(self, neopixel, start, count):
        self.neopixel = neopixel
        self.start = start
        self.stop = self.start + count - 1
        self.count = count
        self.position = 0
        self.run_state = False
        self.blink_state = False
        self.color_on = (0,0,0)
        self.color_default = (0,0,0)
        self.color_off = (0,0,0)
        self.color_blink_on = (0,0,0)
        self.color_blink_off = (0,0,0)
        self.color_half = (0,0,0)
        self.color_show = (0,0,0)
        self.color_value = (0,0,0)

    def set_color_on(self, color_on):
        self.color_on = color_on

    def set_color_def(self, color_default):
        self.color_default = color_default
        
    def set_color_off(self, color_off):
        self.color_off = color_off

    def set_color_value(self, color_value):
        self.color_value = color_value

    def set_color_show(self, color_value):
        self.color_show = color_value

    def set_color_blink_off(self, color_value):
        self.color_blink_off = color_value

    def set_color_blink_on(self, color_value):
        self.color_blink_on = color_value
    
    def set_color_half(self, color_value):
        self.color_half = color_value

    def set_pixel(self, pixel_num, color=None):
        if color:
            self.color_value = color
        else:
            self.color_value = self.color_show
        self.neopixel.set_pixel(self.start + pixel_num, self.color_value)

    def show_on(self):
        self.color_show = self.color_on
        self.blink_state = False
        self.set_line()

    def show_def(self):
        self.color_show = self.color_default
        self.blink_state = False
        self.set_line()

    def show_off(self):
        self.color_show = self.color_off
        self.blink_state = False
        self.set_line()

    def show_half(self):
        self.color_show = self.color_half
        self.blink_state = False
        self.set_line()

    def show_blink(self):
        self.blink_state = True
        if ledstate.get_blink():
            self.color_show = self.color_blink_on
        else:
            self.color_show = self.color_blink_off
        self.set_line()

    def get_blink_state(self):
        return self.blink_state

    def set_line(self):
        self.neopixel.set_pixel_line(self.start, self.stop, self.color_show)

    def show_stripe(self):
        self.neopixel.show()


def setup_ws2812():

    global strip_obj
    global led_obj
    global ledstate
    global mg
    
    mg = MyGlobal
    
    led_obj = []
    strip_obj = []

    ledstate = LedState()
    
    # WS2812 Pins -> Pin 2 - Pin 9

    strip_obj.append(module_neopixel.Neopixel(mg.numpix_1, 0, 2, "GRB"))
    strip_obj.append(module_neopixel.Neopixel(mg.numpix_2, 1, 3, "GRB"))
    strip_obj.append(module_neopixel.Neopixel(mg.numpix_3, 2, 4, "GRB"))
    strip_obj.append(module_neopixel.Neopixel(mg.numpix_4, 3, 5, "GRB"))
    strip_obj.append(module_neopixel.Neopixel(mg.numpix_5, 4, 6, "GRB"))
    strip_obj.append(module_neopixel.Neopixel(mg.numpix_6, 5, 7, "GRB"))
    
    # =========================================================================

    led_obj.append(Ledsegment(strip_obj[mg.seg_01_strip], mg.seg_01_start, mg.seg_01_count))      #  ( 0) -> LED Boden 1
    led_obj.append(Ledsegment(strip_obj[mg.seg_02_strip], mg.seg_02_start, mg.seg_02_count))      #  ( 1) -> LED Boden 2
    led_obj.append(Ledsegment(strip_obj[mg.seg_03_strip], mg.seg_03_start, mg.seg_03_count))      #  ( 2) -> LED Boden 3
    led_obj.append(Ledsegment(strip_obj[mg.seg_04_strip], mg.seg_04_start, mg.seg_04_count))      #  ( 3) -> LED Boden 4
    led_obj.append(Ledsegment(strip_obj[mg.seg_05_strip], mg.seg_05_start, mg.seg_05_count))      #  ( 4) -> LED Boden 5
    led_obj.append(Ledsegment(strip_obj[mg.seg_06_strip], mg.seg_06_start, mg.seg_06_count))      #  ( 5) -> LED Spiegel
    led_obj.append(Ledsegment(strip_obj[mg.seg_07_strip], mg.seg_07_start, mg.seg_07_count))      #  ( 6) -> LED Laser
    led_obj.append(Ledsegment(strip_obj[mg.seg_08_strip], mg.seg_08_start, mg.seg_08_count))      #  ( 7) -> LED Empfänger
    # led_obj.append(Ledsegment(strip_obj[mg.seg_09_strip], mg.seg_09_start, mg.seg_09_count))      #  2, 2  (09) -> LED Position -> # 09 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_10_strip], mg.seg_10_start, mg.seg_10_count))      #  3, 0  (10) -> LED Position -> # 10 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_11_strip], mg.seg_11_start, mg.seg_11_count))      #  3, 1  (11) -> LED Position -> # 11 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_12_strip], mg.seg_12_start, mg.seg_12_count))      #  3, 2  (12) -> LED Position -> # 12 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_13_strip], mg.seg_13_start, mg.seg_13_count))      #  4, 0  (13) -> LED Position -> # 13 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_14_strip], mg.seg_14_start, mg.seg_14_count))      #  5, 0  (14) -> LED Position -> # 14 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_15_strip], mg.seg_15_start, mg.seg_15_count))      #  1, 2  (15) -> LED Position -> # 03 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_16_strip], mg.seg_16_start, mg.seg_16_count))      #  1, 3  (16) -> LED Position -> # 04 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_17_strip], mg.seg_17_start, mg.seg_17_count))      #  1, 4  (17) -> LED Position -> # 05 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_18_strip], mg.seg_18_start, mg.seg_18_count))      #  1, 5  (18) -> LED Position -> # 06 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_19_strip], mg.seg_19_start, mg.seg_19_count))      #  1, 6  (19) -> LED Position -> # 07 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_20_strip], mg.seg_20_start, mg.seg_20_count))      #  1, 7  (20) -> LED Position -> # 08 #--
    # led_obj.append(Ledsegment(strip_obj[mg.seg_21_strip], mg.seg_21_start, mg.seg_21_count))      #  2, 0  (21) -> LED Position -> # 01 #--
    # led_obj.append(Ledsegment(strip_obj[mg.seg_22_strip], mg.seg_22_start, mg.seg_22_count))      #  2, 1  (22) -> LED Position -> # 02 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_23_strip], mg.seg_23_start, mg.seg_23_count))      #  2, 2  (23) -> LED Position -> # 03 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_24_strip], mg.seg_24_start, mg.seg_24_count))      #  2, 3  (24) -> LED Position -> # 04 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_25_strip], mg.seg_25_start, mg.seg_25_count))      #  2, 4  (25) -> LED Position -> # 05 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_26_strip], mg.seg_26_start, mg.seg_26_count))      #  2, 5  (26) -> LED Position -> # 06 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_27_strip], mg.seg_27_start, mg.seg_27_count))      #  2, 6  (27) -> LED Position -> # 07 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_28_strip], mg.seg_28_start, mg.seg_28_count))      #  2, 7  (28) -> LED Position -> # 08 #--
    # led_obj.append(Ledsegment(strip_obj[mg.seg_29_strip], mg.seg_29_start, mg.seg_29_count))      #  3, 0  (29) -> LED Position -> # 01 #--
    # led_obj.append(Ledsegment(strip_obj[mg.seg_30_strip], mg.seg_30_start, mg.seg_30_count))      #  3, 1  (30) -> LED Position -> # 02 #
    # led_obj.append(Ledsegment(strip_obj[mg.seg_31_strip], mg.seg_31_start, mg.seg_31_count))      #  3, 2  (31) -> LED Position -> # 03 #--
    # led_obj.append(Ledsegment(strip_obj[mg.seg_32_strip], mg.seg_32_start, mg.seg_32_count))      #  4, 0  (32) -> LED Position -> # 01 #--
    # led_obj.append(Ledsegment(strip_obj[mg.seg_33_strip], mg.seg_33_start, mg.seg_33_count))      #  5, 0  (33) -> LED Position -> # 01 #--

    for strips in strip_obj:
        strips.brightness(255)
   
    # Alle Leds auf Vorgabewert -> aus
    for strips in strip_obj:
        strips.set_pixel_line(0, strips.num_leds - 1, mg.color_off)
    for strips in strip_obj:
        strips.show()

    # Setze Farbwerte in alle LED-Objekte
    for leds in led_obj:
        leds.set_color_off(mg.color_off)
        leds.set_color_def(mg.color_def)
        leds.set_color_on(mg.color_on)
        leds.set_color_value(mg.color_dot)
        leds.set_color_show(mg.color_dot)
        leds.set_color_blink_off(mg.color_blink_off)
        leds.set_color_blink_on(mg.color_blink_on)
        leds.set_color_half(mg.color_half)
    
    # Blinken aus
    do_all_no_blink()

def test_led(stripe, pos):
    do_all_off()
    strip_obj[stripe].set_pixel(pos, (70,70,70))
    ledstate.refresh()

def do_all_on():
    # Setze Farbwerte in alle LED-Objekte
    for leds in led_obj:
        leds.show_on()
    ledstate.refresh()

def do_all_off():
    # Setze Farbwerte in alle LED-Objekte
    for leds in led_obj:
        leds.show_off()
    ledstate.refresh()

def do_all_def():
    # Setze Farbwerte in alle LED-Objekte
    for leds in led_obj:
        leds.show_def()
    ledstate.refresh()

def do_all_no_blink():
    for leds in led_obj:
        leds.blink_state = False

def do_blink():
    ledstate.do_blink()
    for leds in led_obj:
        if leds.get_blink_state():
            leds.show_blink()
        else:
            pass
    
    ledstate.set(True)
    ledstate.refresh()

def do_test_on():
    #print("Test on")
    led_obj[0].show_on()
    led_obj[1].show_on()
    ledstate.set(True)
 
def do_test_off():
    #print("Test off")
    led_obj[0].show_off()
    led_obj[1].show_off()
    ledstate.set(True)

def do_refresh():

    ledstate.refresh()

def do_get_state():

    return ledstate.get()

def set_all_off():                          # Setze Farbwerte in alle LED-Objekte
    # Setze Farbwerte in alle LED-Objekte
    for leds in led_obj:
        leds.show_off()
    ledstate.refresh()

def set_all_def():                          # Setze Farbwerte in alle LED-Objekte
    for leds in led_obj:
        leds.show_def()
    ledstate.refresh()

def set_all_on():                           # Setze Farbwerte in alle LED-Objekte
    for leds in led_obj:
        leds.show_def()
    ledstate.refresh()

def self_test():                                # Pro Stripe einmal Aus-RGB(25%) -Aus 
    for strips in strip_obj:
        # Alle Aus
        strips.set_pixel_line(0, strips.num_leds - 1, (0,0,0))
        strips.show()
        time.sleep(0.3)
        # Alle Rot
        strips.set_pixel_line(0, strips.num_leds - 1, (50,0,0))
        strips.show()
        time.sleep(0.3)
        # Alle Grün
        strips.set_pixel_line(0, strips.num_leds - 1, (0,50,0))
        strips.show()
        time.sleep(0.3)
        # Alle Blau
        strips.set_pixel_line(0, strips.num_leds - 1, (0,0,50))
        strips.show()
        time.sleep(0.3)
        # Alle Aus
        strips.set_pixel_line(0, strips.num_leds - 1, (0,0,0))
        strips.show()
        time.sleep(0.3)


def do_blink_test():
    loops = 4
    looptime = 0.15
    #print(len(led_obj))
    for x in range(len(led_obj)):
        led_obj[x].show_blink()
        for i in range(loops):
            do_blink()
            time.sleep(looptime)
        led_obj[x].show_off()
        do_refresh()
    

def do_obj_on_off_def_off():
    
    delay_time = 0.3
    for x in range(len(led_obj)):
        led_obj[x].show_on()
        do_refresh()
        time.sleep(delay_time)
        led_obj[x].show_off()
        do_refresh()
        time.sleep(delay_time)
        led_obj[x].show_def()
        do_refresh()
        time.sleep(delay_time)
        led_obj[x].show_off()
        do_refresh()

def do_dot_test():
    delay_time = 0.2
    color_now = (0,10,60)
    for y in range(len(led_obj)):
        for x in range(led_obj[y].count):
            if x > 0:
                led_obj[y].set_pixel(x - 1, (0,0,0))
            led_obj[y].set_pixel(x, color_now)
            do_refresh()
            time.sleep(delay_time)
        led_obj[y].show_off()
        do_refresh()
        time.sleep(delay_time)
        
def set_led_obj(obj,state):
    if state == "off":
        led_obj[obj].show_off()
    if state == "def":
        led_obj[obj].show_def()
    if state == "on":
        led_obj[obj].show_on()
    if state == "half":
        led_obj[obj].show_half()
    if state == "blink":
        led_obj[obj].show_blink()
    do_refresh()

# -----------------------------------------------------------------------------

def main():
    
    print("WS2812 -> Start of Program !!!")

    print("WS2812 -> Setup")
    setup_ws2812()
        
    print("WS2812 -> Run self test")
    self_test()
    
    #print("WS2812 -> Test -> LED")
    #test_led(0,0)

    print("WS2812 -> Object Test")
    do_obj_on_off_def_off()

    #print("WS2812 -> LED-Dot-Test")
    #do_dot_test()

    print("WS2812 -> Segment-Blink")
    do_blink_test()
        
    

    print("WS2812 -> End of Program !!!")

# End

#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
