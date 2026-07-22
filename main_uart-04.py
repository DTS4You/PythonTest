import sys
import uasyncio as asyncio
import select

class CommandParser:
    def __init__(self, name="CLI"):
        self.name = name
        self.commands = {}

    def register(self, path: str, callback, help_text=""):
        """Registriert einen Befehlspfad (z.B. 'led set color')"""
        parts = path.strip().split()
        if not parts:
            return

        current = self.commands
        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {
                    "callback": None,
                    "help": "",
                    "subcommands": {}
                }
            
            # Am Ende des Pfades den Callback und Hilfetext hinterlegen
            if i == len(parts) - 1:
                current[part]["callback"] = callback
                current[part]["help"] = help_text
            
            current = current[part]["subcommands"]

    def print_help(self, current=None, prefix=""):
        """Generiert rekursiv eine saubere Hilfe-Übersicht"""
        if current is None:
            current = self.commands
            print(f"\n--- {self.name} Befehlsübersicht ---")
        
        for name, node in current.items():
            full_cmd = f"{prefix} {name}".strip()
            if node["callback"]:
                help_str = f" - {node['help']}" if node["help"] else ""
                print(f"  {full_cmd:<25}{help_str}")
            
            if node["subcommands"]:
                self.print_help(node["subcommands"], full_cmd)

    async def execute(self, command_string: str):
        """Analysiert den String, trennt Argumente und führt den Befehl aus"""
        parts = command_string.strip().split()
        if not parts:
            return

        current = self.commands
        last_matched_callback = None
        args = []
        
        for i, part in enumerate(parts):
            if part in current:
                node = current[part]
                last_matched_callback = node["callback"]
                current = node["subcommands"]
            else:
                # Ab hier beginnen die Argumente für den letzten erkannten Befehl
                args = parts[i:]
                break
        
        if last_matched_callback:
            try:
                # Prüfen, ob der Callback synchron oder asynchron ist
                res = last_matched_callback(args)
                if hasattr(res, 'send') or hasattr(res, '__next__'):  # Coroutine / Generator
                    await res
            except Exception as e:
                print(f"\nFehler bei der Ausführung: {e}")
        else:
            print(f"\nUnbekannter Befehl: '{' '.join(parts)}'. Tippe 'help' für eine Liste.")

async def cli_reader_task(parser: CommandParser):
    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)
    
    buffer = ""
    print(f"\n{parser.name} bereit. Tippe 'help' für Optionen.")
    sys.stdout.write("> ")
    
    while True:
        # Prüfen, ob Daten im Buffer der seriellen Schnittstelle liegen (Timeout 10ms)
        if poll.poll(10):
            char = sys.stdin.read(1)
            
            # Enter-Taste (CR oder LF)
            if char in ('\r', '\n'):
                cmd = buffer.strip()
                if cmd:
                    sys.stdout.write("\n") # Neue Zeile auf Terminal ausgeben
                    if cmd == "help":
                        parser.print_help()
                    else:
                        await parser.execute(cmd)
                    buffer = ""
                sys.stdout.write("\n> ")
            
            # Backspace / Delete (Terminal-spezifisch)
            elif char in ('\x08', '\x7f'):
                if len(buffer) > 0:
                    buffer = buffer[:-1]
                    sys.stdout.write("\b \b") # Zeichen auf dem Terminal löschen
            
            # Normales Zeichen anhängen und auf dem Terminal spiegeln (Echo)
            else:
                buffer += char
                sys.stdout.write(char)
                
        # Ermöglicht anderen asynchronen Tasks das Arbeiten
        await asyncio.sleep(0.01)

# --- 1. Callbacks definieren ---

# Einfacher synchroner Callback
def cb_sys_reboot(args):
    import machine
    print("System startet neu...")
    machine.reset()

def cb_sys_break(args):
    import sys
    print("System wird unterbrochen. Beende das Programm...")
    sys.exit()

def cb_sys_info(args):
    import gc
    import os
    print(f"Plattform: {sys.platform}")
    print(f"Freier RAM: {gc.mem_free()} Bytes")

# Asynchroner Callback (z.B. für sanftes Einblenden von LEDs)
async def cb_led_set(args):
    if len(args) < 3:
        print("Fehler: Benötige R G B Werte (z.B. 'led set 255 0 0')")
        return
    try:
        r, g, b = int(args[0]), int(args[1]), int(args[2])
        print(f"Setze LED auf R:{r} G:{g} B:{b}")
        # Hier könnte ein sanfter Übergang via uasyncio.sleep() stehen...
        await asyncio.sleep_ms(50) 
    except ValueError:
        print("Fehler: Ungültige Zahlenwerte.")

def cb_set_color(args):
    if len(args) < 4:
        print("Fehler: Benötige Farbindex und R G B Werte (z.B. 'set color 0 255 0 0')")
        return
    try:
        index = int(args[0])
        r, g, b = int(args[1]), int(args[2]), int(args[3])
        print(f"Setze Index: {index} mit Farbwert R:{r} G:{g} B:{b}")
    except ValueError:
        print("Fehler: Ungültige Zahlenwerte.")

def cb_do_all(args):
    if len(args) < 3:
        print("Fehler: Benötige Modus (z.B. 'do all on')")
        return
    try:
        index = int(args[0])
        r, g, b = int(args[0]), int(args[1]), int(args[2])
        print(f"Setze Index: {index} mit Farbwert R:{r} G:{g} B:{b}")
    except ValueError:
        print("Fehler: Ungültige Zahlenwerte.")

def cb_do_obj(args):
    if len(args) < 4:
        print("Fehler: Benötige Index und Modus (z.B. 'do obj 2 on')")
        return
    try:
        index = int(args[0])
        modus= int(args[1])
        print(f"Objekt: {index} auf Modus: {modus}")
    except ValueError:
        print("Fehler: Ungültige Zahlenwerte.")

def cb_test_led(args):
    if len(args) < 4:
        print("Fehler: Benötige Index und Modus (z.B. 'test led 3 on')")
        return
    try:
        index = int(args[0])
        modus= int(args[1])
        print(f"Objekt: {index} auf Modus: {modus}")
    except ValueError:
        print("Fehler: Ungültige Zahlenwerte.")

# --- 2. Parser aufbauen und registrieren ---

parser = CommandParser("MyRP2040-Controller")

# Strukturierte Pfade registrieren
parser.register("sys reboot", cb_sys_reboot, "Startet den Mikrocontroller neu")
parser.register("sys info", cb_sys_info, "Zeigt Speicher- und Plattform-Infos")
parser.register("sys break", cb_sys_break, "Setzt das System zurück")
parser.register("do all", cb_do_all, "Alle LEDs auf Wert <x> setzen")
parser.register("do obj", cb_do_obj, "Objekt: <n> mit Modus: <m> ausführen")
parser.register("test led", cb_test_led, "Test LED: <n> mit Modus: <m> ")
parser.register("set color", cb_set_color, "Setze Farbindex: <i> auf Farbwert: <R> <G> <B>")
parser.register("led set", cb_led_set, "Setzt LED-Farbe: <R> <G> <B>")



# --- 3. Hintergrund-Task simulieren ---

async def background_heartbeat():
    """Simuliert eine parallele Hardware-Aufgabe (z.B. Status-LED blinken)"""
    while True:
        # Hier läuft dein Hauptprogramm ungestört weiter
        await asyncio.sleep(1)


# --- 4. Main Loop starten ---

async def main():
    # CLI Reader und Hintergrund-Tasks parallel starten
    await asyncio.gather(
        cli_reader_task(parser),
        background_heartbeat()
    )

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nProgramm beendet.")
