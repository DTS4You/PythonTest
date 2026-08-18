# slave_ack.py

from machine import Pin
from micropython import schedule

RX_SIZE = 128


class SlaveBus:

    def __init__(
        self,
        data_pins=(2,3,4,5),
        wr_pin=6,
        ack_pin=7
    ):

        self.data = [
            Pin(p, Pin.IN)
            for p in data_pins
        ]

        self.wr = Pin(
            wr_pin,
            Pin.IN,
            Pin.PULL_UP
        )

        self.ack = Pin(
            ack_pin,
            Pin.OUT,
            value=1
        )

        self.rx = bytearray(RX_SIZE)

        self.rx_wr = 0
        self.rx_rd = 0

        self.have_low = False
        self.low_nibble = 0

        self.wr.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self._wr_irq
        )

    def _read_nibble(self):

        v = 0

        for i in range(4):

            if self.data[i].value():
                v |= (1 << i)

        return v

    def _put_rx(self,value):

        next_pos = (
            self.rx_wr + 1
        ) % RX_SIZE

        if next_pos == self.rx_rd:
            return

        self.rx[self.rx_wr] = value
        self.rx_wr = next_pos

    def _wr_irq(self,pin):

        nibble = self._read_nibble()

        #
        # ACK sofort setzen
        #
        self.ack.value(0)

        if not self.have_low:

            self.low_nibble = nibble
            self.have_low = True

        else:

            byte_value = (
                (nibble << 4)
                | self.low_nibble
            )

            self.have_low = False

            self._put_rx(byte_value)

            schedule(
                self._received,
                byte_value
            )

    def _received(self,value):
        pass

    def wr_released(self):

        self.ack.value(1)

    def available(self):

        if self.rx_wr >= self.rx_rd:
            return self.rx_wr - self.rx_rd

        return RX_SIZE - self.rx_rd + self.rx_wr

    def read_byte(self):

        if self.rx_rd == self.rx_wr:
            return None

        v = self.rx[self.rx_rd]

        self.rx_rd = (
            self.rx_rd + 1
        ) % RX_SIZE

        return v

