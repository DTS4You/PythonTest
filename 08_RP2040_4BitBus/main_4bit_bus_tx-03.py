import asyncio
import time
from machine import Pin


class ParallelByteSenderAsync:

    def __init__(self, data_pins, pin_high, pin_low):
        """data_pins: Liste von 4 Pin-Nummern [D0, D1, D2, D3]

        pin_high: Steuerleitung für High-Nibble (Bit 7..4) pin_low:
        Steuerleitung für Low-Nibble (Bit 3..0)
        """
        self.data_pins = [Pin(p, Pin.OUT, value=0) for p in data_pins]
        self.strobe_high = Pin(pin_high, Pin.OUT, value=0)
        self.strobe_low = Pin(pin_low, Pin.OUT, value=0)

    def _write_nibble(self, nibble):
        for i in range(4):
            self.data_pins[i].value((nibble >> i) & 0x01)

    async def send_byte(self, byte_val, pulse_us=20):
        """Sendet 1 Byte (High-Nibble über STROBE_HIGH, Low-Nibble über

        STROBE_LOW).
        """
        high_nibble = (byte_val >> 4) & 0x0F
        low_nibble = byte_val & 0x0F

        # --- 1. High-Nibble übertragen ---
        self._write_nibble(high_nibble)
        time.sleep_us(2)  # Leitungen einschwingen lassen
        self.strobe_high.value(1)
        await asyncio.sleep_ms(0)  # Yield an den Event-Loop
        time.sleep_us(pulse_us)
        self.strobe_high.value(0)

        await asyncio.sleep_ms(0)

        # --- 2. Low-Nibble übertragen ---
        self._write_nibble(low_nibble)
        time.sleep_us(2)
        self.strobe_low.value(1)
        await asyncio.sleep_ms(0)
        time.sleep_us(pulse_us)
        self.strobe_low.value(0)

        await asyncio.sleep_ms(0)

    async def send_bytes(self, data_bytes, delay_ms=2):
        """Sendet ein bytes-Objekt oder ein bytearray mit einstellbarer Pause

        zwischen Bytes.
        """
        for b in data_bytes:
            await self.send_byte(b)
            if delay_ms > 0:
                await asyncio.sleep_ms(delay_ms)


# =====================================================================
# Beispielszenario: Sender-Loop
# =====================================================================

PINS_DATA = [10, 11, 12, 13]  # D0, D1, D2, D3
PIN_STROBE_HIGH = 14  # Strobe für Bit 7..4
PIN_STROBE_LOW = 15   # Strobe für Bit 3..0


async def sender_task(sender):
    counter = 0
    while True:
        # 1. Text-Nachricht senden
        print("Send Byte")
        await sender.send_byte(0xAA)
        await asyncio.sleep(0.3)
        print("Send Byte")
        await sender.send_byte(0x55)
        counter += 1
        await asyncio.sleep(0.3)  # 2 Sekunden Pause bis zum nächsten Paket


async def heartbeat_task():
    """Demonstriert die Asynchronität während der Übertragung."""
    while True:
        # print("[Heartbeat] Event-Loop läuft...")
        await asyncio.sleep(1)


async def main():
    sender = ParallelByteSenderAsync(
        PINS_DATA, PIN_STROBE_HIGH, PIN_STROBE_LOW
    )

    tx_task = asyncio.create_task(sender_task(sender))
    hb_task = asyncio.create_task(heartbeat_task())

    try:
        await asyncio.gather(tx_task, hb_task)
    except asyncio.CancelledError:
        pass


# Sauberer Start & Abbruch per CTRL-C
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n[INFO] Sender durch CTRL-C gestoppt.")