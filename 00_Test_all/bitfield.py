import uctypes

# Basisadresse für unser "Register"
# In echt würde man hier z. B. eine Hardware-Adresse oder ein bytearray nehmen
data = bytearray(4)  # 4 Byte = 32 Bit

# Definition des Bitfeldes
# Wir verwenden LAYOUT = uctypes.LITTLE_ENDIAN für kleine Endianness-Systeme
layout = {
    "FLAG_A": 0 | uctypes.BFUINT32 | (0 << uctypes.BF_POS) | (1 << uctypes.BF_LEN),  # Bit 0
    "FLAG_B": 0 | uctypes.BFUINT32 | (1 << uctypes.BF_POS) | (1 << uctypes.BF_LEN),  # Bit 1
    "MODE":   0 | uctypes.BFUINT32 | (2 << uctypes.BF_POS) | (3 << uctypes.BF_LEN),  # Bits 2-4
    "VALUE":  0 | uctypes.BFUINT32 | (5 << uctypes.BF_POS) | (11 << uctypes.BF_LEN), # Bits 5-15
}

# Erzeuge eine Struktur
reg = uctypes.struct(uctypes.addressof(data), layout, uctypes.LITTLE_ENDIAN)

# Nutzung
print("Initial:", data)

# Setze einzelne Felder
reg.FLAG_A = 1
reg.FLAG_B = 0
reg.MODE = 5      # passt in 3 Bits
reg.VALUE = 1234  # passt in 11 Bits

print("FLAG_A =", reg.FLAG_A)
print("FLAG_B =", reg.FLAG_B)
print("MODE   =", reg.MODE)
print("VALUE  =", reg.VALUE)

print("Raw data:", [hex(b) for b in data])
