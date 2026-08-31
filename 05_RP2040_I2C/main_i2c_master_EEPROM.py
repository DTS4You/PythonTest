from machine import Pin, I2C
import time

PAGE_SIZE = 64
EEPROM_ADDR = 0x50

# sda_pin=20, scl_pin=21

i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)

def write_eeprom_bytes(addr, data):
    """
    Schreibt beliebige Byte-Mengen unter Berücksichtigung der 64-Byte
    Page-Grenzen und der erforderlichen Schreibpausen in den EEPROM.
    """
    total_len = len(data)
    offset = 0
    
    while offset < total_len:
        current_addr = addr + offset
        
        # Berechnen, wie viele Bytes in die aktuelle Page passen
        page_offset = current_addr % PAGE_SIZE
        bytes_left_in_page = PAGE_SIZE - page_offset
        bytes_to_write = min(total_len - offset, bytes_left_in_page)
        
        # Header: 16-Bit-Adresse (High-Byte, Low-Byte)
        header = bytes([(current_addr >> 8) & 0xFF, current_addr & 0xFF])
        chunk = data[offset : offset + bytes_to_write]
        
        # Adresse + Daten in einer I2C-Übertragung senden
        i2c.writeto(EEPROM_ADDR, header + chunk)
        
        # Internen Schreibzyklus des EEPROMs abwarten (5 ms)
        time.sleep_ms(5)
        
        offset += bytes_to_write

def read_eeprom_bytes(addr, length):
    """Liest 'length' Bytes ab der 16-Bit-Speicheradresse 'addr' aus."""
    mem_addr = bytes([(addr >> 8) & 0xFF, addr & 0xFF])
    i2c.writeto(EEPROM_ADDR, mem_addr, False)
    return i2c.readfrom(EEPROM_ADDR, length)

def print_hex_dump(data, start_addr=0):
    """Gibt die Daten als Übersicht aus."""
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        print(f"{start_addr + i:04X}:  {hex_str:<47}  |{ascii_str}|")

# --- Demonstration ---
if EEPROM_ADDR in i2c.scan():
    print("EEPROM gefunden!\n")
    
    # Text zum Schreiben (z. B. 100 Bytes, geht über eine Page-Grenze hinaus)
    test_text = "Hallo RP2040! " * 7  # 98 Bytes
    test_data = test_text.encode('utf-8')
    
    start_address = 0x0030  # Start nahe der Page-Grenze (0x003F) zum Testen
    
    print(f"Schreibe {len(test_data)} Bytes ab Adresse 0x{start_address:04X}...")
    write_eeprom_bytes(start_address, test_data)
    
    print("Lese Daten zurück:\n")
    read_data = read_eeprom_bytes(start_address, len(test_data))
    print_hex_dump(read_data, start_addr=start_address)
else:
    print("Kein I2C-Gerät gefunden.")

