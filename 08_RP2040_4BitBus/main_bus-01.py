import asyncio
from libs.parallel_bus import ParallelBus

# Bus-Instanz erstellen
bus = ParallelBus(
    data_pins=[10, 11, 12, 13], pin_strobe_high=14, pin_strobe_low=15
)


def on_string_received(text):
    print(f"\n[RX Event] Empfangener Text: '{text}' (Länge: {len(text)})")


async def main():
    print("RP2040 Bus aktiv (Modul geladen). Waiting for data...")

    # Empfänger-Task aus der Modul-Klasse starten
    asyncio.create_task(bus.listen_loop(on_string_received))

    counter = 0
    while True:
        # Beispiel: Senden nach Bedarf ausführen
        # await bus.send_text("Hallo RP2040")

        counter += 1
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nProgramm gestoppt.")

