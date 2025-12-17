######################################################
### Main-Program                                   ###
### Projekt: Python Test                           ###
### Version: 0.99                                  ###
### Datum  : 11.08.2025                            ###
######################################################

from machine import Pin
import time

button = Pin(24, Pin.IN, Pin.PULL_UP)

def button_pressed(pin):
    print("Button Pressed!")

# Attach the interrupt to the button's rising edge
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)


while True:
    print("Wait")
    time.sleep(0.5)
