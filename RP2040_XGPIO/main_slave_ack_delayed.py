from slave_ack_delayed import SlaveBus
from utime import sleep_ms

class MySlave(SlaveBus):

    def application_callback(
        self,
        value
    ):

        #
        # Simuliert langsame Verarbeitung
        #
        sleep_ms(50)

        print(
            "Empfangen:",
            hex(value),
            chr(value)
        )

slave = MySlave()

while True:
    pass

