import asyncio
import time
from machine import Pin

# =====================================================================
# HARDWARE-KONFIGURATION (Pull-Up Modus)
# =====================================================================

DATA_PIN_NUMS = [10, 11, 12, 13]  # D0, D1, D2, D3
PIN_NUM_STROBE_HIGH = 14          # Steuerleitung High-Nibble
PIN_NUM_STROBE_LOW = 15           # Steuerleitung Low-Nibble

# Pins initialisieren mit PULL_UP (Ruhezustand: HIGH / 1)
pins_data = [Pin(p, Pin.IN, Pin.PULL_UP) for p in DATA_PIN_NUMS]
strobe_high = Pin(PIN_NUM_STROBE_HIGH, Pin.IN, Pin.PULL_UP)
strobe_low = Pin(PIN_NUM_STROBE_LOW, Pin.IN, Pin.PULL_UP)


# =====================================================================
# EMPFÄNGER (Nicht-blockierend, Active-LOW Pulse)
# =====================================================================

def read_nibble():
    """Liest die 4 Datenleitungen (GP10..GP13) ein."""
    val = 0
    for i in range(4):
        val |= pins_data[i].value() << i
    return val


async def wait_strobe(pin, timeout_ms=100):
    """Wartet mit Timeout auf ein LOW-Signal (0) an einem Strobe-Pin."""
    start = time.ticks_ms()
    while pin.value() == 1:
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            return False
        await asyncio.sleep_ms(2)
    return True


async def read_byte_non_blocking():
    """Liest ein einzelnes Byte über LOW-Strobe-Pulse ein."""
    # 1. High-Nibble empfangen (Warten auf LOW auf GP14)
    if not await wait_strobe(strobe_high, timeout_ms=100):
        return None
    high = read_nibble()
    # Warten bis Signal wieder auf HIGH geht (Ende des 2ms Pulses)
    while strobe_high.value() == 0:
        await asyncio.sleep_ms(1)

    # 2. Low-Nibble empfangen (Warten auf LOW auf GP15)
    if not await wait_strobe(strobe_low, timeout_ms=100):
        return None
    low = read_nibble()
    # Warten bis Signal wieder auf HIGH geht
    while strobe_low.value() == 0:
        await asyncio.sleep_ms(1)

    return (high << 4) | low


async def receiver_loop(on_message_callback):
    """Liest Bytes im Hintergrund und übergibt fertige Strings (bei '\r') an den Callback."""
    buffer = bytearray()

    while True:
        byte = await read_byte_non_blocking()

        if byte is not None:
            if byte == 13:  # ASCII 13 = '\r' (Carriage Return) -> Ende
                text = buffer.decode("utf-8", "ignore")
                buffer.clear()
                on_message_callback(text)
            else:
                buffer.append(byte)

        await asyncio.sleep_ms(5)


# =====================================================================
# SENDER (Active-LOW Pulse mit 2ms Impulsdauer)
# =====================================================================

async def send_nibble(nibble, strobe_pin):
    """Schreibt ein Nibble und erzeugt einen 2ms LOW-Puls."""
    for i in range(4):
        pins_data[i].value((nibble >> i) & 1)

    strobe_pin.value(0)
    await asyncio.sleep_ms(2)  # 2 ms Strobe-Impuls
    strobe_pin.value(1)
    await asyncio.sleep_ms(1)  # Kurze Pause vor dem nächsten Nibble


async def send_text(text):
    """Schaltet GP10..GP15 temporär auf OUT und sendet einen String inkl. '\r'."""
    for p in pins_data:
        p.init(Pin.OUT)
    strobe_high.init(Pin.OUT, value=1)
    strobe_low.init(Pin.OUT, value=1)

    data = text.encode("utf-8") + b"\r"
    for byte in data:
        await send_nibble((byte >> 4) & 0x0F, strobe_high)
        await send_nibble(byte & 0x0F, strobe_low)

    for p in pins_data:
        p.init(Pin.IN, Pin.PULL_UP)
    strobe_high.init(Pin.IN, Pin.PULL_UP)
    strobe_low.init(Pin.IN, Pin.PULL_UP)


# =====================================================================
# MAIN
# =====================================================================

def on_string_received(text):
    print(f"\n[RX Event] Text empfangen: '{text}' (Länge: {len(text)})")


async def main():
    print("RP2040 Bus aktiv (Pins 10-13 Data, 14-15 Strobe, Pull-Up, 2ms Puls).")
    print("Warte auf Daten...")

    asyncio.create_task(receiver_loop(on_string_received))

    counter = 0
    while True:
        counter += 1
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nProgramm gestoppt.")

