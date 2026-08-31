import asyncio
from machine import Pin


class ParallelByteReceiverAsync:

    def __init__(self, data_pins, pin_high, pin_low):
        # Datenpins als Input mit Pull-Down
        self.data_pins = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in data_pins]

        # Strobe-Leitungen als Input mit Pull-Down
        self.strobe_high = Pin(pin_high, Pin.IN, Pin.PULL_DOWN)
        self.strobe_low = Pin(pin_low, Pin.IN, Pin.PULL_DOWN)

    def _read_nibble(self):
        val = 0
        for i in range(4):
            val |= self.data_pins[i].value() << i
        return val

    async def _wait_for_strobe_high(self, timeout_ms):
        """Wartet asynchron auf eine steigende Flanke an STROBE_HIGH (ohne IRQ)."""
        start = asyncio.ticks_ms() if hasattr(asyncio, "ticks_ms") else None
        
        while self.strobe_high.value() == 0:
            if timeout_ms is not None:
                # Polling Timeout-Prüfung
                if start is not None:
                    if asyncio.ticks_diff(asyncio.ticks_ms(), start) > timeout_ms:
                        return False
            # Gibt Steuerung kurz an den asyncio-Loop ab
            await asyncio.sleep_ms(0)
        return True

    async def _wait_for_strobe_low(self, timeout_ms):
        """Wartet asynchron auf eine steigende Flanke an STROBE_LOW (ohne IRQ)."""
        start = asyncio.ticks_ms() if hasattr(asyncio, "ticks_ms") else None
        
        while self.strobe_low.value() == 0:
            if timeout_ms is not None:
                if start is not None:
                    if asyncio.ticks_diff(asyncio.ticks_ms(), start) > timeout_ms:
                        return False
            await asyncio.sleep_ms(0)
        return True

    async def receive_byte(self, timeout_ms=5000):
        """Empfängt ein Einzelbyte über Polling der Strobe-Pins."""
        # 1. High-Nibble Strobe abwarten
        if not await self._wait_for_strobe_high(timeout_ms):
            return None
        high_nibble = self._read_nibble()

        # Abwarten bis STROBE_HIGH wieder abfällt (Flanke freigeben)
        while self.strobe_high.value() == 1:
            await asyncio.sleep_ms(0)

        # 2. Low-Nibble Strobe abwarten
        if not await self._wait_for_strobe_low(timeout_ms):
            raise OSError("Timeout: Low-Nibble Signal verpasst.")
        low_nibble = self._read_nibble()

        # Abwarten bis STROBE_LOW wieder abfällt
        while self.strobe_low.value() == 1:
            await asyncio.sleep_ms(0)

        return (high_nibble << 4) | low_nibble

    async def receive_bytes(self, max_length=64, terminator=b"=", timeout_ms=5000):
        buffer = bytearray()
        
        while len(buffer) < max_length:
            byte_in = await self.receive_byte(timeout_ms=timeout_ms)
            
            if byte_in is None:
                break
                
            buffer.append(byte_in)

            if terminator is not None and byte_in == terminator[0]:
                break

        return bytes(buffer) if buffer else None

    async def receive_string(
        self,
        max_length=64,
        terminator=b"=",
        timeout_ms=5000,
        encoding="utf-8",
        strip_cr=True
    ):
        """Empfängt Bytes und konvertiert sie direkt in einen String."""
        data = await self.receive_bytes(max_length, terminator, timeout_ms)
        if data:
            try:
                text = data.decode(encoding)
            except UnicodeError:
                text = data.decode(encoding, "ignore")
            
            if strip_cr and text.endswith("="):
                text = text[:-1]
                
            return text
        return None


# =====================================================================
# Hauptprogramm
# =====================================================================

PINS_DATA = [10, 11, 12, 13]  # D0, D1, D2, D3
PIN_STROBE_HIGH = 14  # High-Nibble Strobe
PIN_STROBE_LOW = 15  # Low-Nibble Strobe


async def receiver_task(receiver):
    print("Empfänger bereit (Polling-Modus)... Wartet auf Daten mit '\\r'")
    while True:
        text_in = await receiver.receive_string(
            max_length=128,
            terminator=b"=",
            timeout_ms=5000,
            strip_cr=True
        )
        
        if text_in is not None:
            print(f"[RX Text] Empfangen: '{text_in}' (Länge: {len(text_in)})")
        
        await asyncio.sleep_ms(10)


async def main():
    receiver = ParallelByteReceiverAsync(
        PINS_DATA, PIN_STROBE_HIGH, PIN_STROBE_LOW
    )

    rx_task = asyncio.create_task(receiver_task(receiver))

    try:
        await asyncio.gather(rx_task)
    except asyncio.CancelledError:
        pass


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nProgramm gestoppt.")