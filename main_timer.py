import uasyncio as asyncio
from machine import Timer, Pin
import time

# Onboard-LED für optisches Feedback
led = Pin(25, Pin.OUT)

# Flag zur sicheren Kommunikation zwischen Hardware-ISR und asyncio erstellen
event_flag = asyncio.ThreadSafeFlag()


# --- 1. Die Hardware-Timer Interrupt-Service-Routine (ISR) ---
def timer_isr(timer):
    """
    Hardware-Interrupt: Wird exakt alle 100 ms von der Hardware aufgerufen.
    Hier KEINE langen Berechnungen oder Speicher-Allokationen durchführen!
    """
    # Setzt das Flag und weckt die wartende asyncio-Task auf.
    # .set() ist absolut sicher für ISR-Aufrufe.
    event_flag.set()


# --- 2. Die asyncio-Task für die eigentliche Arbeit ---
async def verarbeite_timer_event():
    """
    Wartet asynchron auf das Flag und führt die schwere/komplexe Arbeit aus.
    """
    zaehler = 0
    
    while True:
        # Task pausiert hier völlig speicherschonend, bis timer_isr event_flag.set() aufruft
        await event_flag.wait()
        
        # --- AB HIER: Vollständiger Hauptschleifen-Kontext ---
        # Du kannst jetzt sicher I2C/SPI lesen, Speicher allokieren, printen usw.
        zaehler += 1
        led.toggle()
        print(f"[{time.ticks_ms()} ms] Timer-Event #{zaehler} verarbeitet!")


# --- 3. Weitere parallele asyncio-Tasks (Beispiel) ---
async def hintergrund_task():
    """Zeigt, dass andere Tasks ungestört weiterlaufen."""
    while True:
        # Läuft völlig unabhängig alle 500 ms
        await asyncio.sleep_ms(500)


# --- 4. Hauptprogramm & Event-Loop ---
async def main():
    print("Starte Hardware-Timer + uasyncio Event-Loop...")
    
    # asyncio-Task starten, die auf das Flag wartet
    asyncio.create_task(verarbeite_timer_event())
    asyncio.create_task(hintergrund_task())
    
    # Hardware-Timer initialisieren (100 ms Intervall)
    timer = Timer(-1)
    timer.init(period=100, mode=Timer.PERIODIC, callback=timer_isr)
    
    # Event-Loop am Leben halten
    while True:
        await asyncio.sleep(1)


# Starten
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nProgramm beendet.")

