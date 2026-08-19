###############################################################################
### Module: module_anim_obj.py
###############################################################################
class ANIM_OBJ:
    def __init__(self, stripe, start, lenght, pattern):
        self.stripe     = stripe
        self.start      = start
        self.lenght     = lenght
        self.pattern    = pattern
        self.position   = 0
        self.modifyed   = False


class ANIM_PATTERN:
    def __init__(self, led_pattern, color_index_1, color_index_2=None, color_index_3=None):
        self.led_pattern    = led_pattern
        self.color_index_1  = color_index_1
        self.color_index_2  = color_index_2
        self.color_index_3  = color_index_3
        self.lenght         = len(self.led_pattern)





def main():

    anim_pattern_1 = ANIM_PATTERN([1,2,3,2,1],11,12,13)
    anim_pattern_2 = ANIM_PATTERN([1,2],5,8)

    print("--- Start ---")

    anim_obj = []

    print("Objekte erzeugen")
    anim_obj.append(ANIM_OBJ(1,1,10,anim_pattern_1))
    anim_obj.append(ANIM_OBJ(2,1,10,anim_pattern_2))

    anim_obj[1].modifyed = True

    print("Anzahl der Anim_Objekte:", len(anim_obj))
    print(anim_obj[0].pattern.lenght)
    print(anim_obj[1].pattern.lenght)

    for i in range(len(anim_obj)):
        print("Objekt:", i ,"Modified:", anim_obj[i].modifyed)


    string = ""
    for i in range(10):
        string = string + "0"

    print(string)
    print("LEDSTREIEFN: " + "-" + string + "-")

    print("--- Ende ---")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

