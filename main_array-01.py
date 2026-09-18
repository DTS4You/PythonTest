from array import array

class LEDS:
    def __init__(self, numbers):
        self.pixels = array('I', [0] * numbers)
        self.value = 5

leds = LEDS(10)


pattern_1 = array('I', [10,20,10])
pattern_2 = array('I', [30,40,30])

stripe = leds.pixels

print(f"Pattern: {pattern_1}")
print(f"Pattern: {pattern_2}")

print(f"Input  : {stripe}")


stripe[0:3] = pattern_1
stripe[3:3] = pattern_2

print(f"Output : {stripe}")
