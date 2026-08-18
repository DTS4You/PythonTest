from machine import Pin
from micropython import schedule

RX_FIFO_SIZE = 64
TX_FIFO_SIZE = 64


class IRQBusSlave:

    def __init__(
        self,
        data_pins=(2, 3, 4, 5),
        wr_pin=6,
        rd_pin=7
    ):

        self.data = [Pin(p, Pin.IN) for p in data_pins]

        self.wr = Pin(wr_pin, Pin.IN, Pin.PULL_UP)
        self.rd = Pin(rd_pin, Pin.IN, Pin.PULL_UP)

        #
        # RX FIFO
        #
        self.rx_fifo = bytearray(RX_FIFO_SIZE)

        self.rx_wr = 0
        self.rx_rd = 0

        #
        # TX FIFO
        #
        self.tx_fifo = bytearray(TX_FIFO_SIZE)

        self.tx_wr = 0
        self.tx_rd = 0

        #
        # Empfangsstatus
        #
        self.rx_low_nibble = 0
        self.rx_half_received = False

        #
        # Sendestatus
        #
        self.tx_current_byte = 0
        self.tx_upper_pending = False

        #
        # IRQ registrieren
        #
        self.wr.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self._wr_irq
        )

        self.rd.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            handler=self._rd_irq
        )

    # --------------------------------------------------
    # Datenbus
    # --------------------------------------------------

    def _bus_input(self):
        for p in self.data:
            p.init(Pin.IN)

    def _bus_output(self):
        for p in self.data:
            p.init(Pin.OUT)

    def _read_nibble(self):

        value = 0

        for i in range(4):
            if self.data[i].value():
                value |= (1 << i)

        return value

    def _write_nibble(self, value):

        value &= 0x0F

        for i in range(4):
            self.data[i].value(
                (value >> i) & 1
            )

    # --------------------------------------------------
    # RX FIFO
    # --------------------------------------------------

    def _rx_put(self, value):

        next_pos = (
            self.rx_wr + 1
        ) % RX_FIFO_SIZE

        if next_pos == self.rx_rd:
            return

        self.rx_fifo[self.rx_wr] = value
        self.rx_wr = next_pos

    def available(self):

        if self.rx_wr >= self.rx_rd:
            return self.rx_wr - self.rx_rd

        return RX_FIFO_SIZE - self.rx_rd + self.rx_wr

    def read_byte(self):

        if self.rx_rd == self.rx_wr:
            return None

        value = self.rx_fifo[self.rx_rd]

        self.rx_rd = (
            self.rx_rd + 1
        ) % RX_FIFO_SIZE

        return value

    # --------------------------------------------------
    # TX FIFO
    # --------------------------------------------------

    def send_byte(self, value):

        next_pos = (
            self.tx_wr + 1
        ) % TX_FIFO_SIZE

        if next_pos == self.tx_rd:
            return False

        self.tx_fifo[self.tx_wr] = value

        self.tx_wr = next_pos

        return True

    def send_bytes(self, data):

        for b in data:
            self.send_byte(b)

    def _tx_get(self):

        if self.tx_rd == self.tx_wr:
            return 0

        value = self.tx_fifo[self.tx_rd]

        self.tx_rd = (
            self.tx_rd + 1
        ) % TX_FIFO_SIZE

        return value

    # --------------------------------------------------
    # IRQ WR
    # --------------------------------------------------

    def _wr_irq(self, pin):

        nibble = self._read_nibble()

        if not self.rx_half_received:

            self.rx_low_nibble = nibble
            self.rx_half_received = True

        else:

            byte_value = (
                (nibble << 4)
                | self.rx_low_nibble
            )

            self.rx_half_received = False

            self._rx_put(byte_value)

            schedule(
                self._byte_received,
                byte_value
            )

    def _byte_received(self, value):
        pass

    # --------------------------------------------------
    # IRQ RD
    # --------------------------------------------------

    def _rd_irq(self, pin):

        #
        # RD LOW
        #
        if pin.value() == 0:

            if not self.tx_upper_pending:

                self.tx_current_byte = (
                    self._tx_get()
                )

                nibble = (
                    self.tx_current_byte
                    & 0x0F
                )

                self.tx_upper_pending = True

            else:

                nibble = (
                    self.tx_current_byte >> 4
                ) & 0x0F

                self.tx_upper_pending = False

            self._bus_output()

            self._write_nibble(
                nibble
            )

        #
        # RD HIGH
        #
        else:

            self._bus_input()

