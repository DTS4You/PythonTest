import time
import uasyncio as asyncio
from machine import Pin


class AsyncParallelBusSender:

    def __init__(self, data_pins, req_pin, ack_pin):
        """data_pins: [D0, D1, D2, D3] GP-Nummern

        req_pin: OUT-Pin (Request) ack_pin: IN-Pin (Acknowledge)
        """
        self.data_pins = [Pin(p, Pin.OUT) for p in data_pins]
        self.req = Pin(req_pin, Pin.OUT, value=0)
        self.ack = Pin(ack_pin, Pin.IN, Pin.PULL_DOWN)

    def _write_nibble(self, nibble):
        for i in range(4):
            self.data_pins[i].value((nibble >> i) & 0x01)

    async def send_nibble(self, nibble, timeout_ms=1000):
        """Sendet ein 4-Bit-Nibble asynchron per REQ/ACK Handshake."""
        self._write_nibble(nibble & 0x0F)
        await asyncio.sleep_us(2)  # Kurze Einschwingzeit

        # 1. REQ HIGH
        self.req.value(1)

        # 2. Asynchron warten bis ACK HIGH wird
        start = time.ticks_ms()
        while self.ack.value() == 0:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                self.req.value(0)
                raise TimeoutError("Timeout: Empfänger reagiert nicht (ACK).")
            await asyncio.sleep_ms(0)  # Kontrolle an Event-Loop abgeben

        # 3. REQ LOW
        self.req.value(0)

        # 4. Asynchron warten bis ACK LOW wird
        start = time.ticks_ms()
        while self.ack.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                raise TimeoutError("Timeout: Empfänger setzt ACK nicht zurück.")
            await asyncio.sleep_ms(0)

    async def send_byte(self, byte_val):
        """Sendet 1 Byte (2 Nibbles: High zuerst)."""
        await self.send_nibble((byte_val >> 4) & 0x0F)
        await self.send_nibble(byte_val & 0x0F)

    async def send_bytes(self, data_bytes):
        """Sendet eine Byte-Sequenz."""
        for b in data_bytes:
            await self.send_byte(b)


class AsyncParallelBusReceiver:

    def __init__(self, data_pins, req_pin, ack_pin):
        """data_pins: [D0, D1, D2, D3] GP-Nummern

        req_pin: IN-Pin (Request) ack_pin: OUT-Pin (Acknowledge)
        """
        self.data_pins = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in data_pins]
        self.req = Pin(req_pin, Pin.IN, Pin.PULL_DOWN)
        self.ack = Pin(ack_pin, Pin.OUT, value=0)

    def _read_nibble(self):
        val = 0
        for i in range(4):
            val |= self.data_pins[i].value() << i
        return val

    async def receive_nibble(self, timeout_ms=5000):
        """Empfängt ein 4-Bit-Nibble asynchron."""
        # 1. Asynchron warten bis REQ HIGH wird
        start = time.ticks_ms()
        while self.req.value() == 0:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return None  # Timeout / keine Daten vorhanden
            await asyncio.sleep_ms(0)

        # 2. Daten lesen
        nibble = self._read_nibble()

        # 3. ACK HIGH
        self.ack.value(1)

        # 4. Asynchron warten bis REQ LOW wird
        start = time.ticks_ms()
        while self.req.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                self.ack.value(0)
                raise TimeoutError("Timeout: Sender setzt REQ nicht zurück.")
            await asyncio.sleep_ms(0)

        # 5. ACK LOW (Bereit für nächstes Nibble)
        self.ack.value(0)

        return nibble

    async def receive_byte(self, timeout_ms=5000):
        """Empfängt 1 Byte (2 Nibbles)."""
        high = await self.receive_nibble(timeout_ms)
        if high is None:
            return None

        low = await self.receive_nibble(timeout_ms)
        if low is None:
            raise TimeoutError("Inkomplettes Byte empfangen.")

        return (high << 4) | low


# =====================================================================
# Beispiel zur parallelen Ausführung (Sender & Empfänger Tasks)
# =====================================================================

PIN_DATA = [10, 11, 12, 13]
PIN_REQ = 14
PIN_ACK = 15


async def heartbeat():
    """Zeigt, dass die Event-Loop parallel weiterläuft."""
    count = 0
    while True:
        print(f"[Heartbeat] Loop läuft... {count}")
        count += 1
        await asyncio.sleep(1)


async def sender_task():
    sender = AsyncParallelBusSender(PIN_DATA, PIN_REQ, PIN_ACK)
    await asyncio.sleep(2)  # Kurze Pause vor dem Senden

    message = b"RP2040 Async"
    print(f"[Sender] Starte Übertragung von: {message}")

    start_time = time.ticks_ms()
    await sender.send_bytes(message)
    duration = time.ticks_diff(time.ticks_ms(), start_time)

    print(f"[Sender] Übertragung abgeschlossen in {duration} ms.")


async def receiver_task():
    receiver = AsyncParallelBusReceiver(PIN_DATA, PIN_REQ, PIN_ACK)
    print("[Receiver] Warte auf Daten...")

    received_data = bytearray()
    while True:
        byte_in = await receiver.receive_byte(timeout_ms=1000)
        if byte_in is not None:
            received_data.append(byte_in)
            print(
                f"[Receiver] Empfangen: {chr(byte_in)} (Aktuell gesamt: {bytes(received_data)})"
            )
        await asyncio.sleep_ms(10)


async def main():
    # Startet Heartbeat und Empfänger/Sender parallel
    asyncio.create_task(heartbeat())

    # Hier je nach Anwendungsfall den gewünschten Task ausführen:
    # await receiver_task()
    await sender_task()


# asyncio Loop starten
asyncio.run(main())
