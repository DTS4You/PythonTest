from machine import UART, Pin
import _thread
import time

class SerialDualCoreParser:
    def __init__(self, uart_id=0, baudrate=115200, tx_pin=0, rx_pin=1):
        # UART initialisieren (wir setzen einen kleinen Timeout, um nicht zu blockieren)
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=10)
        
        # Interne Puffer und Synchronisation
        self._rx_buffer = ""
        self._latest_command = ""
        self._command_ready = False
        
        # Thread-Lock für sicheren Datenaustausch zwischen Core 0 und Core 1
        self.lock = _thread.allocate_lock()
        
        # Befehls-Wörterbuch
        self.commands = {}
        self.add_command("help", self._default_help)
        self.add_command("?", self._default_help)
        
        # Core 1 starten - dieser kümmert sich ab jetzt um das Einlesen und Auswerten
        _thread.start_new_thread(self._core1_loop, ())

    def _core1_loop(self):
        """ Diese Endlosschleife läuft ausschließlich auf CORE 1 """
        while True:
            # 1. UART Empfang (Ersatz für den fehlenden Interrupt)
            while self.uart.any():
                try:
                    raw_char = self.uart.read(1)
                    
                    if raw_char is not None:
                        char = raw_char.decode('utf-8', 'ignore')
                        
                        if char == '\r' or char == '\n':
                            if self._rx_buffer.strip() and not self._command_ready:
                                with self.lock:
                                    self._latest_command = self._rx_buffer
                                    self._command_ready = True
                            self._rx_buffer = ""
                        else:
                            self._rx_buffer += char
                except Exception:
                    pass

            # 2. Befehlsauswertung direkt auf Core 1
            cmd_line = None
            with self.lock:
                if self._command_ready:
                    cmd_line = self._latest_command
                    self._command_ready = False
            
            if cmd_line:
                parts = cmd_line.strip().split()
                if parts:
                    command = parts[0].lower()
                    args = parts[1:]
                    
                    if command in self.commands:
                        try:
                            # Die Funktion wird auf Core 1 ausgeführt!
                            self.commands[command](args)
                        except Exception as e:
                            self.send(f"ERROR auf Core 1 bei '{command}': {e}")
                    else:
                        self.send(f"ERROR: Befehl '{command}' unbekannt.")
            
            # Ganz kurzes Schlafen, damit der Core nicht heißläuft (ca. 2ms)
            time.sleep_ms(2)

    def _default_help(self, args):
        self.send("Verfuegbare Befehle: " + ", ".join(self.commands.keys()))

    def add_command(self, name, function):
        self.commands[name.lower()] = function

    def send(self, text):
        self.uart.write(text + "\r\n")
