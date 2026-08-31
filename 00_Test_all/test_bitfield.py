import uctypes

# Wir definieren eine Struktur mit Bitfeldern
# Annahme: ein 16-Bit Register (2 Byte)
# Format: (Offset_in_Bytes * 8 + BitPosition, BitLänge | uctypes.BFUINT16)
REGISTER_LAYOUT = {
    "bit_0": 0 | uctypes.BFUINT8 | (0 << uctypes.BF_POS) | (1 << uctypes.BF_LEN),   # Bit 0
    "bit_1": 0 | uctypes.BFUINT8 | (1 << uctypes.BF_POS) | (1 << uctypes.BF_LEN),   # Bit 1
    "bit_2": 0 | uctypes.BFUINT8 | (2 << uctypes.BF_POS) | (1 << uctypes.BF_LEN),   # Bit 2
    "bit_3": 0 | uctypes.BFUINT8 | (3 << uctypes.BF_POS) | (1 << uctypes.BF_LEN),   # Bit 3
}

# Beispiel: Wir legen uns einen Buffer von 2 Bytes an
buf = bytearray(1)

# Struktur an Buffer binden
reg = uctypes.struct(uctypes.addressof(buf), REGISTER_LAYOUT, uctypes.LITTLE_ENDIAN)

# Jetzt können wir mit den Bitfeldern arbeiten
reg.bit_0 = 1       
reg.bit_1 = 0 
reg.bit_2 = 1
reg.bit_3 = 1

# Buffer anzeigen
print("Raw buffer:", [hex(x) for x in buf])
print("Bit_0:", reg.bit_0)
print("Bit_1:", reg.bit_1)
print("Bit_2:", reg.bit_2)
print("Bit_3:", reg.bit_3)
