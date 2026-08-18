from machine import Pin
from utime import ticks_us
from utime import ticks_diff


class MasterBus:

    def __init__(
        self,
        data_pins=(2, 3, 4, 5),
        wr_pin=6,
        ack_pin=7
    ):

        self.data = [
            Pin(
                pin,
                Pin.OUT,
                value=0
            )
            for pin in data_pins
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

        self.ack_received = False

        self.ack.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self._ack_irq
        )

    #################################################
    # ACK IRQ
    #################################################

    def _ack_irq(self, pin):

        self.ack_received = True

    #################################################
    # Nibble senden
    #################################################

    def _write_nibble(self, value):

        value &= 0x0F

        self.data[0].value(value & 0x01)
        self.data[1].value(value & 0x02)
        self.data[2].value(value & 0x04)
        self.data[3].value(value & 0x08)

    def _strobe(self):

        self.wr.value(0)
        self.wr.value(1)

    #################################################
    # ACK warten
    #################################################

    def wait_for_ack(
        self,
        timeout_ms=1000
    ):

        timeout_us = (
            timeout_ms * 1000
        )

        start = ticks_us()

        #
        # ACK LOW abwarten
        #
        while not self.ack_received:

            if ticks_diff(
                ticks_us(),
                start
            ) > timeout_us:

                return False

        #
        # ACK HIGH abwarten
        #
        while self.ack.value() == 0:

            if ticks_diff(
                ticks_us(),
                start
            ) > timeout_us:

                return False

        self.ack_received = False

        return True

    #################################################
    # Byte senden
    #################################################

    def send_byte(
        self,
        value,
        timeout_ms=1000
    ):

        #
        # Low Nibble
        #
        self._write_nibble(
            value & 0x0F
        )

        self._strobe()

        #
        # High Nibble
        #
        self._write_nibble(
            (value >> 4) & 0x0F
        )

        self._strobe()

        #
        # ACK des kompletten Bytes
        #
        return self.wait_for_ack(
            timeout_ms
        )

    #################################################
    # Telegramm senden
    #################################################

    def send_bytes(
        self,
        data,
        timeout_ms=1000
    ):

        for b in data:

            if not self.send_byte(
                b,
                timeout_ms
            ):
                return False

        return True

