class PLC:
    def __init__(self):
        self.state = 'STOP'                 # Zustand der Steuerung
        self.inputs = 0x00
        self.outputs = 0x00
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
    

    def read_input(self, inputs):
        self.inputs = inputs
    
    def write_output(self, outputs):
        self.outputs = outputs

    def cycle(self):
        self.read_input(0x00)
        self.logic()
        self.write_output(0x00)
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
