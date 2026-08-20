# Eingangsdaten als Liste von Dezimalwerten (0 bis 255)
bytes_dec = [0, 1, 1, 1]

# Vorzeichenbehaftet (signed = True)
val_signed = int.from_bytes(bytes(bytes_dec), 'big', signed=True)

# Vorzeichenlos (signed = False)
val_unsigned = int.from_bytes(bytes(bytes_dec), 'big', signed=False)

print("Signed Int32:  ", val_signed)   # Output: 67305985
print("Unsigned Int32:", hex(val_unsigned))