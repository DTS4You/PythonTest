class ANIM_OBJ:
    def __init__(self, stripe, start, lenght, pattern):
        self.stripe     = stripe
        self.start      = start
        self.lenght     = lenght
        self.pattern    = pattern


class ANIM_PATTERN:
    def __init__(self, led_pattern, color_index_1, color_index_2, color_index_3):
        self.led_pattern    = led_pattern
        self.color_index_1  = color_index_1
        self.color_index_2  = color_index_2
        self.color_index_3  = color_index_3
        self.pattern_lenght = len(self.led_pattern)



anim_pattern = ANIM_PATTERN([1,2,3,2,1],11,12,13)

print("Start")

print(anim_pattern.pattern_lenght)

anim_obj = []

anim_obj.append(ANIM_OBJ(1,1,10,anim_pattern))

print("Objekt")

print(anim_obj[0].pattern.color_index_1)

