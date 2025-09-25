from micropython import const

MCP_GPIOA = const(0x12)     # Spiegelt den Wert am Anschluss A wider.
MCP_GPIOB = const(0x13)     # Spiegelt den Wert am Anschluss B wider.

MCP_OLATA = const(0x14)     # Schalte Ausgänge Port A.
MCP_OLATB = const(0x15)     # Schalte Ausgänge Port B.

MCP_IODIRA = const(0x00)    # Steuert die Richtung der Daten-E/A für Anschluss A.
MCP_IODIRB = const(0x01)    # Steuert die Richtung der Daten-E/A für Anschluss B.

MCP_IPOLA = const(0x02)     # Konfiguriert die Polarität der entsprechenden GPIO-Port-Bits für Port A.
MCP_IPOLB = const(0x03)     # Konfiguriert die Polarität der entsprechenden GPIO-Port-Bits für Port B.

MCP_GPINTENA = const(0x04)  # Steuert den Interrupt-on-change für jeden Pin von Anschluss A.
MCP_GPINTENB = const(0x05)  # Steuert den Interrupt-on-change für jeden Pin von Anschluss B.

MCP_DEFVALA = const(0x06)   # Steuert den Standard-Vergleichswert für Interrupt-on-Change für Anschluss A.
MCP_DEFVALB = const(0x07)   # Steuert den Standard-Vergleichswert für Interrupt-on-Change für Anschluss B.

MCP_INTCONA = const(0x08)   # Steuert, wie der zugehörige Pin-Wert für den Interrupt-on-change für Anschluss A verglichen wird.
MCP_INTCONB = const(0x09)   # Steuert, wie der zugehörige Pin-Wert für den Interrupt-on-change für Anschluss B verglichen wird.

MCP_IOCON = const(0x0A)     # Steuert das Gerät

MCP_GPPUA = const(0x0C)     # Schaltet Pull-up-Widerstände für Port A auf 5V
MCP_GPPUB = const(0x0D)     # Schaltet Pull-up-Widerstände für Port B auf 5V

MCP_INTFA = const(0x0E)     # Spiegelt den Unterbrechungszustand an den Pins von Anschluss A wieder
MCP_INTFB = const(0x0F)     # Spiegelt den Unterbrechungszustand an den Pins des Anschluss B wieder

MCP_INTCAPA = const(0x10)   # Erfasst den Wert von Anschluss A zum Zeitpunkt des Auftretens der Unterbrechung
MCP_INTCAPB = const(0x11)   # Erfasst den Wert des Anschlusses B zum Zeitpunkt des Auftretens der Unterbrechung



class MCP23017():
    def __init__(self, i2c, address=0x20):
        self._i2c = i2c
        self._address = address
        self.init()

    def init(self):
        self._write([MCP_IODIRA, 0x00])
        self._write([MCP_IODIRB, 0xFF])
        self._write([MCP_OLATA, 0x00])

    def _read(self, reg, count):
        return self._i2c.readfrom_mem(self._address, reg, count) 

    def _write(self, val):
        self._i2c.writeto(self._address, bytearray(val))
        
    def _write_mem(self, reg, val):
        self._i2c.writeto_mem(self._address, reg, bytearray([val]))
        