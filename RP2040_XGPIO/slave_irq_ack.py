from machine import Pin
from micropython import schedule

RX_FIFO_SIZE = 128


class SlaveBus:

    def __init__(
        self,
        data_pins=(2, 3, 4, 5),
        wr_pin=6,
        ack_pin=7
    ):

        #
        # Datenbus
        #
        self.data = [
            Pin(p, Pin.IN)
            for p in data_pins
        ]

        #
        # Steuerleitungen
        #
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

        #
        # Ringpuffer
        #
        self.rx_fifo = bytearray(
            RX_FIFO_SIZE
        )

        self.rx_wr = 0
        self.rx_rd = 0

        #
        # Byteaufbau
        #
        self.low_nibble = 0
        self.have_low = False

        #
        # WR Interrupt
        #
        self.wr.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self._wr_irq
        )

    #################################################
    # FIFO
    #################################################

    def _put_rx(self, value):

        next_pos = (
            self.rx_wr + 1
        ) % RX_FIFO_SIZE

        if next_pos == self.rx_rd:
            return

        self.rx_fifo[
            self.rx_wr
        ] = value

        self.rx_wr = next_pos

    def available(self):

        if self.rx_wr >= self.rx_rd:
            return (
                self.rx_wr -
                self.rx_rd
            )

        return (
            RX_FIFO_SIZE -
            self.rx_rd +
            self.rx_wr
        )

    def read_byte(self):

        if self.rx_rd == self.rx_wr:
            return None

        value = self.rx_fifo[
            self.rx_rd
        ]

        self.rx_rd = (
            self.rx_rd + 1
        ) % RX_FIFO_SIZE

        return value

    #################################################
    # Datenbus lesen
    #################################################

    def _read_nibble(self):

        value = 0

        for i in range(4):

            if self.data[i].value():

                value |= (
                    1 << i
                )

        return value

    #################################################
    # WR IRQ
    #################################################

    def _wr_irq(self, pin):

        nibble = self._read_nibble()

        #
        # ACK aktiv
        #
        self.ack.value(0)

        if not self.have_low:

            self.low_nibble = nibble
            self.have_low = True

            schedule(
                self._ack_release,
                0
            )

        else:

            byte_value = (
                (nibble << 4)
                | self.low_nibble
            )

            self.have_low = False

            self._put_rx(
                byte_value
            )

            schedule(
                self._byte_received,
                byte_value
            )

    #################################################
    # ACK freigeben
    #################################################

    def _ack_release(self, dummy):

        self.ack.value(1)

    #################################################
    # Byte fertig empfangen
    #################################################

    def _byte_received(self, value):

        #
        # Hier kann beliebige
        # Verarbeitung stattfinden.
        #

        self.ack.value(1)
