from master_ack_byte import MasterBus
from utime import sleep_ms

bus = MasterBus()

counter = 0

while True:

    text = (
        "RP2040-%03d\n"
        % counter
    )

    print(
        "Sende:",
        text.strip()
    )

    ok = bus.send_bytes(
        text.encode(),
        timeout_ms=500
    )

    if ok:
        print("OK")
    else:
        print("Timeout")

    counter += 1

    sleep_ms(1000)

