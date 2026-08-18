# master_ack.py

from machine import Pin
from utime import sleep_us, ticks_us, ticks_diff


class MasterBus:

    def __init__(
        self,
        data_pins=(2,3,4,5),
        wr_pin=6,
        ack_pin=7
    ):

        self.data = [
            Pin(
                p,
                Pin.OUT,
                value=0
            )
            for p in data_pins
        ]

        self.wr = Pin(
            wr_pin,
            Pin.OUT,
            value=1
        )

        self.ack = Pin(
            ack_pin,
            Pin.IN,
            Pin.PULL_UP
        )

    def _write_nibble(self,n):

        for i in range(4):

            self.data[i].value(
                (n >> i) & 1
            )

    def send_nibble(
        self,
        nibble,
        timeout_us=50000
    ):

        self._write_nibble(
            nibble & 0x0F
        )

        self.wr.value(0)

        start = ticks_us()

        #
        # ACK warten
        #
        while self.ack.value():

            if ticks_diff(
                    ticks_us(),
                    start
               ) > timeout_us:

                return False

        self.wr.value(1)

        #
        # Auf ACK Freigabe warten
        #
        start = ticks_us()

        while not self.ack.value():

            if ticks_diff(
                    ticks_us(),
                    start
               ) > timeout_us:

                return False

        return True

    def send_byte(self,b):

        if not self.send_nibble(
            b & 0x0F
        ):
            return False

        if not self.send_nibble(
            (b >> 4) & 0x0F
        ):
            return False

        return True


