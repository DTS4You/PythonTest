import time
import uasyncio as asyncio
from machine import Pin

# Abfangen, falls TimeoutError in der verwendeten MicroPython-Version fehlt
try:
    TimeoutError
except NameError:

    class TimeoutError(Exception):
        pass


class InterruptParallelBusSender:

    def __init__(self, data_pins, req_pin, ack_pin):
        self.data_pins = [Pin(p, Pin.OUT) for p in data_pins]
        self.req = Pin(req_pin, Pin.OUT, value=0)
        self.ack = Pin(ack_pin, Pin.IN, Pin.PULL_DOWN)

        # Signal-Flag für Thread-sichere Benachrichtigung aus dem IRQ
        self.ack_flag = asyncio.ThreadSafeFlag()
        self.ack.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._on_ack_change)

    def _on_ack_change(self, pin):
        """Hardware IRQ Callback für Zustandsänderungen an ACK."""
        self.ack_flag.set()

    def _write_nibble(self, nibble):
        for i in range(4):
            self.data_pins[i].value((nibble >> i) & 0x01)

    async def _wait_for_ack(self, target_state, timeout_ms):
        """Wartet rein Event-basiert per IRQ auf den Zielzustand von ACK."""
        start = time.ticks_ms()
        while self.ack.value() != target_state:
            remaining = timeout_ms - time.ticks_diff(time.ticks_ms(), start)
            if remaining <= 0:
                raise TimeoutError(f"Timeout beim Warten auf ACK={target_state}")

            try:
                # Blockselbsthaltung aufgeben, bis ein IRQ auftritt
                await asyncio.wait_for(self.ack_flag.wait(), remaining / 1000.0)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Timeout beim Warten auf ACK={target_state}")

    async def send_nibble(self, nibble, timeout_ms=1000):
        # 1. Daten anlegen
        self._write_nibble(nibble & 0x0F)
        time.sleep_us(2)

        # 2. REQ HIGH setzen
        self.req.value(1)

        # 3. Per IRQ warten, bis Empfänger ACK HIGH setzt
        await self._wait_for_ack(1, timeout_ms)

        # 4. REQ LOW setzen
        self.req.value(0)

        # 5. Per IRQ warten, bis Empfänger ACK wieder auf LOW zieht
        await self._wait_for_ack(0, timeout_ms)

    async def send_byte(self, byte_val):
        await self.send_nibble((byte_val >> 4) & 0x0F)
        await self.send_nibble(byte_val & 0x0F)

    async def send_bytes(self, data_bytes):
        for b in data_bytes:
            await self.send_byte(b)


class InterruptParallelBusReceiver:

    def __init__(self, data_pins, req_pin, ack_pin):
        self.data_pins = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in data_pins]
        self.req = Pin(req_pin, Pin.IN, Pin.PULL_DOWN)
        self.ack = Pin(ack_pin, Pin.OUT, value=0)

        # Signal-Flag für Thread-sichere Benachrichtigung aus dem IRQ
        self.req_flag = asyncio.ThreadSafeFlag()
        self.req.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._on_req_change)

    def _on_req_change(self, pin):
        """Hardware IRQ Callback für Zustandsänderungen an REQ."""
        self.req_flag.set()

    def _read_nibble(self):
        val = 0
        for i in range(4):
            val |= self.data_pins[i].value() << i
        return val

    async def _wait_for_req(self, target_state, timeout_ms):
        """Wartet rein Event-basiert per IRQ auf den Zielzustand von REQ."""
        start = time.ticks_ms()
        while self.req.value() != target_state:
            remaining = timeout_ms - time.ticks_diff(time.ticks_ms(), start)
            if remaining <= 0:
                return False

            try:
                await asyncio.wait_for(self.req_flag.wait(), remaining / 1000.0)
            except asyncio.TimeoutError:
                return False
        return True

    async def receive_nibble(self, timeout_ms=5000):
        # 1. Per IRQ warten, bis REQ HIGH wird
        if not await self._wait_for_req(1, timeout_ms):
            return None

        # 2. Daten einlesen
        nibble = self._read_nibble()

        # 3. ACK HIGH setzen
        self.ack.value(1)

        # 4. Per IRQ warten, bis Sender REQ auf LOW setzt
        if not await self._wait_for_req(0, timeout_ms):
            self.ack.value(0)
            #raise TimeoutError("Timeout: Sender setzt REQ nicht zurück.")

        # 5. ACK LOW setzen
        self.ack.value(0)
        return nibble

    async def receive_byte(self, timeout_ms=5000):
        high = await self.receive_nibble(timeout_ms)
        if high is None:
            return None

        low = await self.receive_nibble(timeout_ms)
        if low is None:
            raise TimeoutError("Inkomplettes Byte empfangen.")

        return (high << 4) | low


# =====================================================================
# Beispielanwendung
# =====================================================================

PIN_DATA = [10, 11, 12, 13]
PIN_REQ = 14
PIN_ACK = 15


async def heartbeat():
    count = 0
    while True:
        print(f"[System OK] Heartbeat {count}")
        count += 1
        await asyncio.sleep(1)


async def receiver_task():
    receiver = InterruptParallelBusReceiver(PIN_DATA, PIN_REQ, PIN_ACK)
    print("[Receiver IRQ] Warte auf Daten...")

    received_buffer = bytearray()
    while True:
        byte_in = await receiver.receive_byte(timeout_ms=3000)
        if byte_in is not None:
            received_buffer.append(byte_in)
            print(f"[Receiver IRQ] Zeichen empfangen: {chr(byte_in)}")

async def sender_task():
    # Sender mit den gleichen Pins wie oben initialisieren
    sender = InterruptParallelBusSender(PIN_DATA, PIN_REQ, PIN_ACK)

    # Kurze Pause, damit der Empfänger bereit ist
    await asyncio.sleep(2)

    data_to_send = b"RP2040 Interrupt"
    print(f"[Sender IRQ] Starte Senden von: {data_to_send}")

    start_time = time.ticks_ms()

    try:
        # Sendet die Bytes event-basiert über Hardware-IRQs
        await sender.send_bytes(data_to_send)
        duration = time.ticks_diff(time.ticks_ms(), start_time)
        print(f"[Sender IRQ] Erfolgreich gesendet in {duration} ms!")

    except TimeoutError as e:
        print(f"[Sender IRQ] Fehler: {e}")


async def main():
    # Heartbeat läuft völlig unabhängig im Hintergrund weiter
    asyncio.create_task(heartbeat())

    # Starte entweder den Empfänger ODER den Sender:

    # 1) Wenn dieser RP2040 als Empfänger agiert:
    await receiver_task()

    # 2) Wenn dieser RP2040 als Sender agiert:
    #await sender_task()


asyncio.run(main())