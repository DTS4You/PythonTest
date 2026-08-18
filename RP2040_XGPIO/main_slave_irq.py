from irq_slave import IRQBusSlave
from utime import sleep_ms

bus = IRQBusSlave()

counter = 0

while True:

    #
    # Empfang anzeigen
    #
    while bus.available():

        b = bus.read_byte()

        print(
            "RX:",
            hex(b),
            chr(b)
        )

    #
    # Antwort vorbereiten
    #
    text = "A%03d" % counter

    bus.send_bytes(
        text.encode()
    )

    counter += 1

    sleep_ms(1000)

