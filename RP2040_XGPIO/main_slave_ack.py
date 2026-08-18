from slave_ack import SlaveBus

bus = SlaveBus()

while True:

    if bus.wr.value():
        bus.wr_released()

    while bus.available():

        b = bus.read_byte()

        print(
            "RX:",
            hex(b),
            chr(b)
        )


