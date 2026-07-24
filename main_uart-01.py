from machine import Pin
import time
from serial_parser import SerialDualCoreParser

# --- HARDWARE ---
try:
    led = Pin("LED", Pin.OUT)
except ValueError:
    led = Pin(25, Pin.OUT)

# --- BEFEHLE (Werden auf Core 1 ausgeführt!) ---
def cmd_led(args):
    if not args:
        parser.send("ERROR: Parameter fehlt (on/off)")
        return
    value = args[0].lower()
    print(value)
    if value == "all":
        pass
    action = args[1].lower()
    print(action)
    if action == "on":
        led.value(1)
        parser.send("SUCCESS: LED an")
    elif action == "off":
        led.value(0)
        parser.send("SUCCESS: LED aus")
    else:
        parser.send("ERROR: Unbekannter Parameter")

# --- INITIALISIERUNG ---
# Startet automatisch Core 1 im Hintergrund
parser = SerialDualCoreParser(uart_id=0, baudrate=115200, tx_pin=0, rx_pin=1)
parser.add_command("led", cmd_led)

parser.send("\r\n=== System im Dual-Core-Modus gestartet ===")

# --- HAUPTSCHLEIFE (Läuft komplett ungestört auf CORE 0) ---
while True:
    # Core 0 kann schlafen oder extrem aufwendige Dinge tun.
    # Core 1 kriegt im Hintergrund trotzdem jede UART-Eingabe sofort mit!
    print("[Core 0] Ich arbeite ungestoert...")
    time.sleep(5)
