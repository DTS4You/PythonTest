from master_irq_ack import MasterBus
from utime import sleep_ms

bus = MasterBus()

counter = 0

while True:

    text = (
        "Hallo %03d\n"
        % counter
    )

    print(
        "Sende:",
        text
    )

    bus.send_bytes(
        text.encode()
    )

    counter += 1

    sleep_ms(1000)

    