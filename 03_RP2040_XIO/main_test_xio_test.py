from machine import Pin
from time import sleep

input_pin = Pin(10, Pin.IN)

print(input_pin.value())

