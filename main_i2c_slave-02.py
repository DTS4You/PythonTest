from machine import Pin, I2C, Timer, mem32
import micropython

# Speicherreservierung für IRQ-Sicherheit
micropython.alloc_emergency_exception_buf(100)

class RP2040_I2C_Slave_Background:
    IC_CON          = 0x00
    IC_SAR          = 0x08
    IC_DATA_CMD     = 0x10
    IC_RAW_INTR_STAT= 0x34
    IC_CLR_RD_REQ   = 0x50
    IC_ENABLE       = 0x6C
    IC_STATUS       = 0x9C

    def __init__(self, i2c_id=0, sda_pin=4, scl_pin=5, slave_addr=0x41, timer_id=-1):
        self.base_addr = 0x40044000 if i2c_id == 0 else 0x40048000
        self.rx_callback = None
        self.rd_callback = None

        # Hardware-Initialisierung
        self.dummy_i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=100_000)

        mem32[self.base_addr + self.IC_ENABLE] = 0
        mem32[self.base_addr + self.IC_CON] = 0x02
        mem32[self.base_addr + self.IC_SAR] = slave_addr
        mem32[self.base_addr + self.IC_ENABLE] = 1

        # Periodic Software Timer (-1) als Hintergrund-Schleife (alle 1ms)
        self.timer = Timer(timer_id)
        self.timer.init(period=1, mode=Timer.PERIODIC, callback=self._poll_i2c)

    def _poll_i2c(self, timer):
        stat = mem32[self.base_addr + self.IC_RAW_INTR_STAT]

        # RD_REQ: Master verlangt ein Byte
        if stat & (1 << 5):
            _ = mem32[self.base_addr + self.IC_CLR_RD_REQ]
            tx_byte = 0x00
            if self.rd_callback:
                tx_byte = self.rd_callback()
            mem32[self.base_addr + self.IC_DATA_CMD] = tx_byte & 0xFF

        # RX_FULL: Master hat ein Byte gesendet
        if stat & (1 << 2) or ((mem32[self.base_addr + self.IC_STATUS] & (1 << 3)) != 0):
            rx_byte = mem32[self.base_addr + self.IC_DATA_CMD] & 0xFF
            if self.rx_callback:
                try:
                    micropython.schedule(self.rx_callback, rx_byte)
                except RuntimeError:
                    pass

    def stop(self):
        """Stoppt den Hintergrund-Timer."""
        self.timer.deinit()

import time

counter = 0

def on_data_received(byte):
    print(f"Empfangen: 0x{byte:02X}")

def on_read_requested():
    global counter
    val = counter
    counter = (counter + 1) & 0xFF
    return val

slave = RP2040_I2C_Slave_Background(i2c_id=0, sda_pin=4, scl_pin=5, slave_addr=0x41)
slave.rx_callback = on_data_received
slave.rd_callback = on_read_requested

print("Slave läuft im Hintergrund...")

# Die Hauptschleife bleibt komplett frei
while True:
    time.sleep(1)
