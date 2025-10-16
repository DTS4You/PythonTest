#------------------------------------------------------------------------------
# 4 bytes to int32
byte_array = [0x55,0xAA,0xF0,0x0F]
print(byte_array)
value = int.from_bytes(byte_array, byteorder='big', signed=False)
print(value, hex(value))
#------------------------------------------------------------------------------
# int32 to 4 bytes
byte_array = (value.to_bytes(4, "big", signed=False))

byte_red    = byte_array[0]
byte_green  = byte_array[1]
byte_blue   = byte_array[2]
byte_alpha  = byte_array[3]

int_rgb = (byte_red, byte_green, byte_blue)
print(byte_red, byte_green, byte_blue, byte_alpha)
print(int_rgb, byte_alpha)

