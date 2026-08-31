import machine
import micropython
import time

# Notfall-Puffer einrichten (erlaubt Fehlermeldungen innerhalb von Interrupts)
micropython.alloc_emergency_exception_buf(100)

# Onboard-LED initialisieren
try:
    led = machine.Pin(25, machine.Pin.OUT)
except ValueError:
    led = machine.Pin("LED", machine.Pin.OUT)

# Hardware-UART 0 initialisieren (TX=GP0, RX=GP1)
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))


def uart_action(arg):
    """
    Diese Funktion wird vom Scheduler ausgeführt.
    Hier dürfen wir print(), decode() und uart.write() sicher nutzen!
    """
    if uart.any() > 0:
        data = uart.read(uart.any())
        try:
            text = data.decode('utf-8')
            print(f"Interrupt-Empfang: {text.strip()}")
            uart.write(f"Echo (IRQ): {text}")
        except UnicodeError:
            print(f"Interrupt-Empfang (Bytes): {data}")
            uart.write(data)
            
        # LED kurz als optisches Feedback aufblinken lassen
        led.value(1)
        time.sleep_ms(30)
        led.value(0)


def uart_isr(t):
    """
    Der eigentliche Hardware-Interrupt (ISR = Interrupt Service Routine).
    Muss extrem schnell sein und darf keinen Speicher allozieren.
    """
    # Wir übergeben die schwere Arbeit (uart_action) sofort an den Scheduler
    micropython.schedule(uart_action, None)


# Interrupt an den UART0 binden. 
# Er triggert, sobald Zeichen empfangen werden (machine.UART.RX_ANY)
uart.irq(handler=uart_isr, trigger=machine.UART.RX_ANY)

print("UART-Interrupts erfolgreich eingerichtet!")
uart.write("RP2040 Interrupt-UART bereit!\r\n")

# Das Hauptprogramm ist jetzt komplett frei!
while True:
    # Hier könnte dein Hauptcode stehen.
    # Um zu zeigen, dass die Hauptschleife nicht blockiert ist,
    # lassen wir sie einfach im Hintergrund Däumchen drehen.
    time.sleep(1)