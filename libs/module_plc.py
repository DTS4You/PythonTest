class PLC:
    def __init__(self):
        self.state = 'STOP'                 # Zustand der Steuerung
        self.step_value = 0                 # Ablaufsteuerung Schrittwert
        self.step_max = 5                   # Maximale Schritte Anzahl
        self.inputs = {                     # Eingänge (z.B. Taster, Sensoren)
            'start': False,
            'stop': False,
            'sensor': False
        }
        self.outputs = {                    # Ausgänge (z.B. Motor, Relais)
            'motor': False,
            'alarm': False
        }

    def set_state(self, state='STOP'):
        if state == 'START':
            self.state = 'RUN'
            return self.state
        if state == 'RUN':
            self.state = 'RUN'
            return self.state
        self.state = 'STOP'
        return self.state
    

    def read_input(self):
        # Eingänge vom Benutzer simulieren
        self.inputs['start'] = input("Start-Taster drücken? (ja/nein): ").lower() == 'ja'
        self.inputs['stop'] = input("Stop-Taster drücken? (ja/nein): ").lower() == 'ja'
        self.inputs['sensor'] = input("Sensor aktiviert? (ja/nein): ").lower() == 'ja'
    
    def write_output(self):
        print(f"Motor: {'An' if self.outputs['motor'] else 'Aus'}")
        print(f"Alarm: {'An' if self.outputs['alarm'] else 'Aus'}")
        print(f"Aktueller Zustand: {self.state}")

    def cycle(self):
        self.read_input()
        self.logic()
        self.write_output()
        print("-" * 30)

    def logic(self):
        if self.state == 'RUN':
            print("PLC -> RUN")

def main():
    state = 'RUN'
    plc = PLC()
    print(plc.set_state(state))
    #plc.cycle()

# ###############################################################################
# ### Main                                                                    ###
# ###############################################################################

if __name__ == "__main__":

    main()
