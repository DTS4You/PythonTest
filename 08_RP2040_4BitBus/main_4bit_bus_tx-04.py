import asyncio
import time
from machine import Pin


class ParallelByteSenderAsync:

    def __init__(self, data_pins, pin_high, pin_low):
        """data_pins: [D0, D1, D2, D3]

        pin_high: STROBE_HIGH Output-Pin pin_low: STROBE_LOW Output-Pin
        """
        self.data_pins = [Pin(p, Pin.OUT) for p in data_pins]
        self.strobe_high = Pin(pin_high, Pin.OUT, value=0)
        self.strobe_low = Pin(pin_low, Pin.OUT, value=0)

    def _write_nibble(self, nibble):
        for i in range(4):
            self.data_pins[i].value((nibble >> i) & 0x01)

    async def send_byte(self, byte_val, pulse_us=50):
        """Sendet ein einzelnes Byte über High- und Low-Strobe."""
        high_nibble = (byte_val >> 4) & 0x0F
        low_nibble = byte_val & 0x0F

        # --- 1. High-Nibble senden ---
        self._write_nibble(high_nibble)
        time.sleep_us(5)  # Leitungs-Einschwingzeit
        self.strobe_high.value(1)
        time.sleep_us(pulse_us)  # Pulsdauer
        self.strobe_high.value(0)

        # Kurze Pause für den Empfänger (Gibt dem Polling-Loop Zeit zum Verarbeiten)
        await asyncio.sleep_ms(0)

        # --- 2. Low-Nibble senden ---
        self._write_nibble(low_nibble)
        time.sleep_us(5)
        self.strobe_low.value(1)
        time.sleep_us(pulse_us)
        self.strobe_low.value(0)

        await asyncio.sleep_ms(0)

    async def send_bytes(self, data_bytes, delay_ms=1):
        """Sendet ein bytes- oder bytearray-Objekt."""
        for b in data_bytes:
            await self.send_byte(b)
            if delay_ms > 0:
                await asyncio.sleep_ms(delay_ms)

    async def send_string(self, text, delay_ms=1, encoding="utf-8"):
       
        data = bytearray(text.encode(encoding))
        

        await self.send_bytes(data, delay_ms=delay_ms)


# =====================================================================
# Hauptprogramm (Sender)
# =====================================================================

PINS_DATA = [10, 11, 12, 13]  # D0, D1, D2, D3
PIN_STROBE_HIGH = 14  # High-Nibble Strobe
PIN_STROBE_LOW = 15  # Low-Nibble Strobe


async def sender_task(sender):
    counter = 1
    while True:
        # Nachricht vorbereiten
        msg = f"Hallo RP2040 #{counter}="
        print(f"[TX String] Sende: '{msg}'")

        # String mit automatischem '\\r' am Ende senden
        await sender.send_string(msg, delay_ms=2)

        counter += 1
        await asyncio.sleep(2)  # Alle 2 Sekunden eine Nachricht senden


async def main():
    sender = ParallelByteSenderAsync(
        PINS_DATA, PIN_STROBE_HIGH, PIN_STROBE_LOW
    )

    tx_task = asyncio.create_task(sender_task(sender))

    try:
        await asyncio.gather(tx_task)
    except asyncio.CancelledError:
        pass


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nSender gestoppt.")