class PLC:
    def __init__(self):
        # Eingänge (z.B. Taster, Sensoren)
        self.inputs = {
            'start': False,
            'stop': False,
            'sensor': False
        }
        # Ausgänge (z.B. Motor, Relais)
        self.outputs = {
            'motor': False,
            'alarm': False
        }
        # Zustand der Steuerung
        self.state = 'IDLE'

    def lesen_eingaenge(self):
        # Eingänge vom Benutzer simulieren
        self.inputs['start'] = input("Start-Taster drücken? (ja/nein): ").lower() == 'ja'
        self.inputs['stop'] = input("Stop-Taster drücken? (ja/nein): ").lower() == 'ja'
        self.inputs['sensor'] = input("Sensor aktiviert? (ja/nein): ").lower() == 'ja'

    def steuerung_ablauf(self):
        if self.state == 'IDLE':
            if self.inputs['start']:
                print("Motor startet...")
                self.outputs['motor'] = True
                self.state = 'RUNNING'
        elif self.state == 'RUNNING':
            if self.inputs['stop']:
                print("Motor stoppt...")
                self.outputs['motor'] = False
                self.state = 'IDLE'
            elif self.inputs['sensor']:
                print("Sensor aktiviert! Alarm auslösen.")
                self.outputs['alarm'] = True
            else:
                self.outputs['alarm'] = False

    def ausgabe_anzeigen(self):
        print(f"Motor: {'An' if self.outputs['motor'] else 'Aus'}")
        print(f"Alarm: {'An' if self.outputs['alarm'] else 'Aus'}")
        print(f"Aktueller Zustand: {self.state}")

    def laufen(self):
        while True:
            self.lesen_eingaenge()
            self.steuerung_ablauf()
            self.ausgabe_anzeigen()
            print("-" * 30)

# Hauptprogramm
if __name__ == "__main__":
    plc = PLC()
    plc.laufen()
