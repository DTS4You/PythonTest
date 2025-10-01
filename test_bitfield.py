import uctypes

# Wir definieren eine Struktur mit Bitfeldern
# Annahme: ein 16-Bit Register (2 Byte)
# Format: (Offset_in_Bytes * 8 + BitPosition, BitLänge | uctypes.BFUINT16)
REGISTER_LAYOUT = {
    "flag_a": 0 | uctypes.BFUINT16 | (0 << uctypes.BF_POS) | (1 << uctypes.BF_LEN),   # Bit 0
    "flag_b": 0 | uctypes.BFUINT16 | (1 << uctypes.BF_POS) | (2 << uctypes.BF_LEN),   # Bits 1-2
    "flag_c": 0 | uctypes.BFUINT16 | (3 << uctypes.BF_POS) | (5 << uctypes.BF_LEN),   # Bits 3-7
    "flag_d": 0 | uctypes.BFUINT16 | (8 << uctypes.BF_POS) | (8 << uctypes.BF_LEN),   # Bits 8-15
}

# Beispiel: Wir legen uns einen Buffer von 2 Bytes an
buf = bytearray(2)

# Struktur an Buffer binden
reg = uctypes.struct(uctypes.addressof(buf), REGISTER_LAYOUT, uctypes.LITTLE_ENDIAN)

# Jetzt können wir mit den Bitfeldern arbeiten
reg.flag_a = 1         # Bit 0 setzen
reg.flag_b = 3         # Bits 1-2 auf 11b setzen
reg.flag_c = 15        # Bits 3-7 = 11111
reg.flag_d = 0xAB      # Oberes Byte = 10101011

# Buffer anzeigen
print("Raw buffer:", [hex(x) for x in buf])
print("flag_a:", reg.flag_a)
print("flag_b:", reg.flag_b)
print("flag_c:", reg.flag_c)
print("flag_d:", hex(reg.flag_d))
