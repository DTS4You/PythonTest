from machine import Pin, I2C, mem32
import time

class RP2040_I2C_Slave:
    # Register-Offsets der RP2040 Hardware-I2C-Einheit
    IC_CON          = 0x00
    IC_TAR          = 0x04
    IC_SAR          = 0x08
    IC_DATA_CMD     = 0x10
    IC_RAW_INTR_STAT= 0x34
    IC_CLR_INTR     = 0x40
    IC_CLR_RD_REQ   = 0x50
    IC_CLR_TX_ABRT  = 0x54
    IC_ENABLE       = 0x6C
    IC_STATUS       = 0x9C

    def __init__(self, i2c_id=0, sda_pin=4, scl_pin=5, slave_addr=0x41):
        self.i2c_id = i2c_id
        self.base_addr = 0x40044000 if i2c_id == 0 else 0x40048000
        self.slave_addr = slave_addr

        # Einmalige Initialisierung über MicroPython zur GPIO-Multiplexing- und Takt-Konfiguration
        self.dummy_i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=100_000)

        # Peripheral deaktivieren vor Rekonfiguration
        mem32[self.base_addr + self.IC_ENABLE] = 0

        # Control Register: Master deaktivieren (Bit 0 = 0), Slave aktivieren (Bit 6 = 0), 7-Bit Addr
        mem32[self.base_addr + self.IC_CON] = 0x02

        # Slave-Adresse setzen
        mem32[self.base_addr + self.IC_SAR] = slave_addr

        # Peripheral wieder aktivieren
        mem32[self.base_addr + self.IC_ENABLE] = 1

    def any_read(self):
        """Prüft, ob der Master Daten geschickt hat (RX FIFO nicht leer)."""
        return (mem32[self.base_addr + self.IC_STATUS] & (1 << 3)) != 0

    def read_byte(self):
        """Liest ein empfangenes Byte aus dem Empfangs-FIFO."""
        return mem32[self.base_addr + self.IC_DATA_CMD] & 0xFF

    def write_byte(self, val):
        """Sendet ein Byte an den Master zurück."""
        mem32[self.base_addr + self.IC_DATA_CMD] = val & 0xFF

    def check_requests(self):
        """
        Prüft den Status der I2C-Anfragen vom Master.
        Rückgabe: 'READ_REQ' (Master fordert Daten an), 'WRITE_REQ' (Master hat Daten gesendet) oder None.
        """
        stat = mem32[self.base_addr + self.IC_RAW_INTR_STAT]

        # Bit 5: RD_REQ (Master verlangt ein Byte vom Slave)
        if stat & (1 << 5):
            _ = mem32[self.base_addr + self.IC_CLR_RD_REQ] # Interrupt quittieren
            return "READ_REQ"

        # Bit 2: RX_FULL (Master hat ein Byte an den Slave gesendet)
        if stat & (1 << 2) or self.any_read():
            return "WRITE_REQ"

        return None


# Pin-Belegung: SDA = GPIO 4, SCL = GPIO 5, Adresse = 0x41
slave = RP2040_I2C_Slave(i2c_id=0, sda_pin=20, scl_pin=21, slave_addr=0x41)

counter = 0

print("I2C Slave gestartet auf Adresse 0x41...")

while True:
    req = slave.check_requests()

    if req == "READ_REQ":
        # Master fordert ein Byte an
        slave.write_byte(counter)
        print(f"Gesendet an Master: {counter}")
        counter = (counter + 1) & 0xFF

    elif req == "WRITE_REQ":
        # Master sendet ein Byte
        data = slave.read_byte()
        print(f"Empfangen vom Master: 0x{data:02X} ({data})")

    time.sleep_ms(10)

