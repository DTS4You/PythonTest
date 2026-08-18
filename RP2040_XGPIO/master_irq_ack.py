from machine import Pin
from micropython import schedule


class MasterBus:

    STATE_IDLE = 0
    STATE_WAIT_ACK_LOW = 1
    STATE_WAIT_ACK_HIGH = 2

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
            Pin(
                p,
                Pin.OUT,
                value=0
            )
            for p in data_pins
        ]

        #
        # Steuerleitungen
        #
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

        #
        # TX FIFO
        #
        self.tx_fifo = []

        #
        # Byteaufbau
        #
        self.current_byte = 0

        self.current_nibble = 0

        self.send_high = False

        self.state = self.STATE_IDLE

        #
        # ACK Interrupt
        #
        self.ack.irq(
            trigger=
                Pin.IRQ_FALLING |
                Pin.IRQ_RISING,
            handler=self._ack_irq
        )

    ################################################
    # FIFO
    ################################################

    def send_byte(self, value):
        self.tx_fifo.append(
            value & 0xFF
        )

        self._start_next_transfer()

    def send_bytes(self, data):
        for b in data:
            self.send_byte(b)

    ################################################
    # Hardware
    ################################################

    def _write_nibble(self, value):

        value &= 0x0F

        for i in range(4):

            self.data[i].value(
                (value >> i) & 1
            )

    ################################################
    # Transfer starten
    ################################################

    def _start_next_transfer(self):

        if self.state != self.STATE_IDLE:
            return

        if not self.tx_fifo:
            return

        self.current_byte = (
            self.tx_fifo.pop(0)
        )

        self.send_high = False

        self._send_next_nibble()

    ################################################
    # Nibble senden
    ################################################

    def _send_next_nibble(self):

        if not self.send_high:

            nibble = (
                self.current_byte
                & 0x0F
            )

        else:

            nibble = (
                self.current_byte >> 4
            ) & 0x0F

        self.current_nibble = nibble

        self._write_nibble(
            nibble
        )

        #
        # WR aktivieren
        #
        self.wr.value(0)

        self.state = (
            self.STATE_WAIT_ACK_LOW
        )

    ################################################
    # ACK IRQ
    ################################################

    def _ack_irq(self, pin):

        schedule(
            self._ack_handler,
            pin.value()
        )

    ################################################
    # ACK Verarbeitung
    ################################################

    def _ack_handler(self, level):

        #
        # ACK LOW
        #
        if (
            level == 0 and
            self.state ==
            self.STATE_WAIT_ACK_LOW
        ):

            self.wr.value(1)

            self.state = (
                self.STATE_WAIT_ACK_HIGH
            )

            return

        #
        # ACK HIGH
        #
        if (
            level == 1 and
            self.state ==
            self.STATE_WAIT_ACK_HIGH
        ):

            if not self.send_high:

                #
                # jetzt oberes Nibble
                #
                self.send_high = True

                self._send_next_nibble()

                return

            #
            # Byte komplett
            #
            self.state = self.STATE_IDLE

            self._start_next_transfer()

    ################################################
    # Status
    ################################################

    def busy(self):

        return (
            self.state != self.STATE_IDLE
        )


