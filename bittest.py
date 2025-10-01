

class Byte_Bitfield():
    def __init__(self):
        self.value  = 0x00
        self.bit_   = [False, False, False, False, False, False, False, False]

    def convert(self, value):
        self.value = value
        for i in range(8):
            if (self.value & 1 << i ):
                self.bit_[i] = True
            else:
                self.bit_[i] = False

class Bitfield_Byte():
    def __init__(self):
        self.value  = 0x00
        self.bit_   = [False, False, False, False, False, False, False, False]
    
    def convert(self):
        self.value = 0x00
        for i in range(8):
            if self.bit_[i] == True:
                self.value = self.value | 1 << i
        return self.value


input_bf = Byte_Bitfield()

output_bf = Bitfield_Byte()

input_bf.convert(0xAA)

for i in range(8):
    print(input_bf.bit_[i])

output_bf.bit_[0] = True
output_bf.bit_[2] = True

print(output_bf.convert())

