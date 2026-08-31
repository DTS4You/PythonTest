import asyncio
import time
from machine import Pin


class ParallelByteSenderAsync:

    def __init__(self, data_pins, pin_high, pin_low):
        """data_pins: [D0, D1, D2, D3]

        pin_high: Steuerleitung High-Nibble
        pin_low: Steuerleitung Low-Nibble
        """
        self.data_pins = [Pin(p, Pin.OUT) for p in data_pins]
        self.strobe_high = Pin(pin_high, Pin.OUT, value=0)
        self.strobe_low = Pin(pin_low, Pin.OUT, value=0)

    def _write_nibble(self, nibble):
        for i in range(4):
            self.data_pins[i].value((nibble >> i) & 0x01)

    async def send_byte(self, byte_val, pulse_us=20):
        """Sendet 1 Byte asynchron über die zwei Strobe-Leitungen."""
        high_nibble = (byte_val >> 4) & 0x0F
        low_nibble = byte_val & 0x0F

        # --- High-Nibble ---
        self._write_nibble(high_nibble)
        time.sleep_us(2)  # Kurzes Einschwingen der Leitungen
        self.strobe_high.value(1)
        await asyncio.sleep_ms(0)  # Yield an den Event-Loop
        time.sleep_us(pulse_us)
        self.strobe_high.value(0)

        await asyncio.sleep_ms(0)

        # --- Low-Nibble ---
        self._write_nibble(low_nibble)
        time.sleep_us(2)
        self.strobe_low.value(1)
        await asyncio.sleep_ms(0)
        time.sleep_us(pulse_us)
        self.strobe_low.value(0)

        await asyncio.sleep_ms(0)

    async def send_bytes(self, data_bytes, delay_ms=1):
        """Sendet einen Puffer byteweise asynchron."""
        for b in data_bytes:
            await self.send_byte(b)
            if delay_ms > 0:
                await asyncio.sleep_ms(delay_ms)


class ParallelByteReceiverAsync:

    def __init__(self, data_pins, pin_high, pin_low):
        self.data_pins = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in data_pins]

        # Events für flankengetriggerten Empfang per IRQ
        self.event_high = asyncio.Event()
        self.event_low = asyncio.Event()

        # Pins mit Hardware-Interrupts verbinden
        self.strobe_high = Pin(pin_high, Pin.IN, Pin.PULL_DOWN)
        self.strobe_low = Pin(pin_low, Pin.IN, Pin.PULL_DOWN)

        self.strobe_high.irq(
            trigger=Pin.IRQ_RISING, handler=self._on_strobe_high
        )
        self.strobe_low.irq(trigger=Pin.IRQ_RISING, handler=self._on_strobe_low)

    def _on_strobe_high(self, pin):
        self.event_high.set()

    def _on_strobe_low(self, pin):
        self.event_low.set()

    def _read_nibble(self):
        val = 0
        for i in range(4):
            val |= self.data_pins[i].value() << i
        return val

    async def receive_byte(self, timeout_ms=5000):
        """Wartet ohne CPU-Last auf High- und Low-Strobe."""
        self.event_high.clear()
        self.event_low.clear()

        # 1. Warten auf High-Nibble (mit Timeout)
        try:
            await asyncio.wait_for(self.event_high.wait(), timeout_ms / 1000.0)
        except asyncio.TimeoutError:
            return None

        high_nibble = self._read_nibble()

        # 2. Warten auf Low-Nibble
        try:
            await asyncio.wait_for(self.event_low.wait(), timeout_ms / 1000.0)
        except asyncio.TimeoutError:
            raise OSError("Timeout: Low-Nibble Signal verpasst.")

        low_nibble = self._read_nibble()

        return (high_nibble << 4) | low_nibble

    def close(self):
        """Trennt die Interrupts (Wichtig beim Beenden/Reset)."""
        self.strobe_high.irq(handler=None)
        self.strobe_low.irq(handler=None)


# =====================================================================
# Beispiel-Tasks & Main-Loop mit CTRL-C Handhabung
# =====================================================================

PINS_DATA = [10, 11, 12, 13]
PIN_STROBE_HIGH = 14
PIN_STROBE_LOW = 15


async def receiver_task(receiver):
    print("Receiver läuft... (Wartet auf Daten)")
    while True:
        byte_in = await receiver.receive_byte(timeout_ms=3000)
        if byte_in is not None:
            print(
                f"[RX] Byte empfangen: 0x{byte_in:02X} -> '{chr(byte_in) if 32 <= byte_in <= 126 else '?'}'"
            )
        await asyncio.sleep_ms(10)


async def heartbeat_task():
    """Zeigt, dass der Event-Loop parallel ungehindert weiterläuft."""
    counter = 0
    while True:
        print(f"[Heartbeat] Loop aktiv ({counter})")
        counter += 1
        await asyncio.sleep(1)


async def main():
    receiver = ParallelByteReceiverAsync(
        PINS_DATA, PIN_STROBE_HIGH, PIN_STROBE_LOW
    )

    # Parallel laufende Tasks starten
    rx_task = asyncio.create_task(receiver_task(receiver))
    hb_task = asyncio.create_task(heartbeat_task())

    # Falls dieses Board auch als SENDER testen soll:
    # sender = ParallelByteSenderAsync(PINS_DATA, PIN_STROBE_HIGH, PIN_STROBE_LOW)
    # await sender.send_bytes(b"RP2040 Async!")

    try:
        await asyncio.gather(rx_task, hb_task)
    except asyncio.CancelledError:
        pass
    finally:
        receiver.close()
        print("\n[INFO] Empfänger beendet & IRQs getrennt.")


# Starten mit sauberem Abbruch bei CTRL-C
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nProgramm durch Tastendruck gestoppt.")

