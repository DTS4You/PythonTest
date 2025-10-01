x = 0xff

class Bitfield():
    def __init__(self, value):
        self.value  = value
        self.bit_   = [False, False, False, False, False, False, False, False]

    def convert(self, value):
        self.value = value
        for i in range(8):
            if (self.value & 1 << i ):
                self.bit_[i] = True
            else:
                self.bit_[i] = False


bf = Bitfield(0x00)

bf.convert(0xff)

for i in range(8):
    print(bf.bit_[i])
