###############################################################################
### Module: module_anim_obj.py
###############################################################################
import time

class ANIM_OBJ:
    def __init__(self, stripe, start, lenght, pattern, direction=True):
        self.stripe     = stripe
        self.start      = start
        self.led_lenght = lenght
        self.pattern    = pattern
        self.position   = 0
        self.direction  = direction
        self.modulo     = 0
        self.modifyed   = False
        self.led_array  = self.pattern.led_pattern + [0] * self.led_lenght
        self.arr_lenght = self.led_lenght + self.pattern.lenght
        self.act_array  = self.led_array

    def get_modulo(self):
        self.modulo = self.position % len(self.led_array)

    def get_led_array(self):
        return self.led_array

    def rotate_right(self, n):
        n = n % len(self.led_array)
        return self.led_array[-n:] + self.led_array[:-n]

    def rotate_left(self, n):
        n = n % len(self.led_array)
        return self.led_array[n:] + self.led_array[:n]

    def do_anim_step(self):
        if self.direction:
            self.act_array = self.rotate_right(self.position)
        else:
            self.act_array = self.rotate_left(self.position)

        if self.position >= self.arr_lenght:
            self.position = 0
        else:
            self.position = self.position + 1
        
        return self.act_array[self.pattern.lenght:]                 # Auf echte Anzahl LEDs kürzen -> Pattern vorne entfernen

class ANIM_PATTERN:
    def __init__(self, led_pattern):
        self.led_pattern    = led_pattern
        self.lenght         = len(self.led_pattern)




def main():

    anim_pattern_1 = ANIM_PATTERN([1,2,3,2,1])
    anim_pattern_2 = ANIM_PATTERN([1,2,1])

    print("--- Start ---")

    anim_obj = []

    print("Objekte erzeugen")
    anim_obj.append(ANIM_OBJ(1,1,10,anim_pattern_1,True))
    anim_obj.append(ANIM_OBJ(2,1,10,anim_pattern_2,False))

    anim_obj[1].modifyed = True

    print("Anzahl der Anim_Objekte:", len(anim_obj))
    print(anim_obj[0].pattern.lenght)
    print(anim_obj[1].pattern.lenght)

    #for i in range(len(anim_obj)):
    #    print("Objekt:", i ,"Array:", anim_obj[i].led_array)

    print(anim_obj[0].arr_lenght)

    for i in range(20):
        
        print(f"Objekt: {anim_obj[0].position:02d} Array:", anim_obj[0].do_anim_step())

        time.sleep(0.2)
    

    print("--- Ende ---")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

