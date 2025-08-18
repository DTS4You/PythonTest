# Test
# 18.08.2025
print("Hallo")

class Segment:
    def __init__(self):
        self.stripe     = 1
        self.led_start  = 0
        self.led_stop   = 0
        self.led_num    = 0


NUM_SEGMENTS = 8

segs = [Segment() for dummy in range(NUM_SEGMENTS)]

print(len(segs))

for index in range(len(segs)):
    print(segs[index].stripe)
