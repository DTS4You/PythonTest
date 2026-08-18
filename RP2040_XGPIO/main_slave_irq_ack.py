from slave_irq_ack import SlaveBus

bus = SlaveBus()

print("Slave gestartet")

while True:

    while bus.available():

        b = bus.read_byte()

        print(
            "RX:",
            hex(b),
            chr(b)
        )

