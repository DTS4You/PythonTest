from machine import Pin
from micropython import schedule

FIFO_SIZE = 256


class SlaveBus:

    def __init__(
        self,
        data_pins=(2,3,4,5),
        wr_pin=6,
        ack_pin=7
    ):

        #
        # Datenleitungen
        #
        self.data = [
            Pin(p, Pin.IN)
            for p in data_pins
        ]

        #
        # WR vom Master
        #
        self.wr = Pin(
            wr_pin,
            Pin.IN,
            Pin.PULL_UP
        )

        #
        # ACK an Master
        #
        self.ack = Pin(
            ack_pin,
            Pin.OUT,
            value=1
        )

        #
        # RX FIFO
        #
        self.rx_fifo = bytearray(
            FIFO_SIZE
        )

        self.rx_wr = 0
        self.rx_rd = 0

        #
        # Byteaufbau
        #
        self.have_low = False
        self.low_nibble = 0

        #
        # WR Interrupt
        #
        self.wr.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self._wr_irq
        )

    ################################################
    # FIFO
    ################################################

    def _put_rx(self, value):

        next_wr = (
            self.rx_wr + 1
        ) & 0xFF

        if next_wr == self.rx_rd:
            return

        self.rx_fifo[
            self.rx_wr
        ] = value

        self.rx_wr = next_wr

    def available(self):

        return (
            self.rx_wr -
            self.rx_rd
        ) & 0xFF

    def read_byte(self):

        if self.rx_rd == self.rx_wr:
            return None

        value = self.rx_fifo[
            self.rx_rd
        ]

        self.rx_rd = (
            self.rx_rd + 1
        ) & 0xFF

        return value

    ################################################
    # Datenbus lesen
    ################################################

    def _read_nibble(self):

        value = 0

        if self.data[0].value():
            value |= 0x01

        if self.data[1].value():
            value |= 0x02

        if self.data[2].value():
            value |= 0x04

        if self.data[3].value():
            value |= 0x08

        return value

    ################################################
    # WR IRQ
    ################################################

    def _wr_irq(self, pin):

        nibble = self._read_nibble()

        #
        # erstes Nibble
        #
        if not self.have_low:

            self.low_nibble = nibble
            self.have_low = True

            return

        #
        # Byte fertig
        #
        byte_value = (
            (nibble << 4)
            | self.low_nibble
        )

        self.have_low = False

        #
        # Verarbeitung
        #
        schedule(
            self._process_byte,
            byte_value
        )

    ################################################
    # Byte verarbeiten
    ################################################

    def _process_byte(self, value):

        #
        # ACK aktiv
        #
        self.ack.value(0)

        #
        # Hier darf beliebig lange
        # gearbeitet werden
        #
        self._put_rx(value)

        #
        # Beispiel:
        #
        self.application_callback(
            value
        )

        #
        # ACK freigeben
        #
        self.ack.value(1)

    ################################################
    # Anwendung
    ################################################

    def application_callback(
        self,
        value
    ):
        pass

