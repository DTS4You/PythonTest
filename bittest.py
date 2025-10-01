

class Byte_Bitfield():
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

class Bitfield_Byte():
    def __init__(self, value):
        self.value  = value
        self.bit_   = [False, False, False, False, False, False, False, False]
    
    def convert(self):
        self.value = 0x00
        for i in range(8):
            if self.bit_[i] == True:
                self.value = self.value | 1 << i


input_bf = Byte_Bitfield(0x00)

output_bf = Bitfield_Byte(0x00)

input_bf.convert(0xAA)

for i in range(8):
    print(input_bf.bit_[i])

output_bf.bit_[0] = True
output_bf.bit_[2] = True

output_bf.convert()

print(output_bf.value)

