import uasyncio as asyncio

class UeberwachterWert:
    def __init__(self, startwert):
        self._wert = startwert
        # Event signalisiert Änderungen
        self.geandert_event = asyncio.Event()

    @property
    def wert(self):
        return self._wert

    @wert.setter
    def wert(self, neuer_wert):
        if self._wert != neuer_wert:
            self._wert = neuer_wert
            # Weckt wartende Tasks auf
            self.geandert_event.set()


# --- Anwendung ---

daten = UeberwachterWert(startwert=10)

async def beobachter_task():
    """Wartet passiv, bis sich der Wert ändert."""
    while True:
        # Task pausiert hier speicherschonend, bis geandert_event.set() aufgerufen wird
        await daten.geandert_event.wait()
        
        # Event zurücksetzen für die nächste Änderung
        daten.geandert_event.clear()
        
        print(f"[REAKTION] Der Wert hat sich geändert auf: {daten.wert}")

async def veraenderer_task():
    """Simuliert Änderungen der Variable."""
    await asyncio.sleep(1)
    print("Ändere Wert auf 20...")
    daten.wert = 20  # Löst automatisch das Event aus!

    await asyncio.sleep(2)
    print("Ändere Wert auf 50...")
    daten.wert = 50  # Löst erneut das Event aus!

async def main():
    asyncio.create_task(beobachter_task())
    asyncio.create_task(veraenderer_task())
    
    await asyncio.sleep(5)

asyncio.run(main())

