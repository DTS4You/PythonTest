from machine import Pin, PWM
from utime import sleep

# Set GPIO pin for audio output
buzzer = PWM(Pin(15))

def play_tone(frequency):
    # Set maximum volume
    buzzer.duty_u16(1000)
    # Play tone
    buzzer.freq(frequency)

def be_quiet():
    # Set minimum volume
    buzzer.duty_u16(0)

## Infinite loop
while True:
    play_tone(65)
    sleep(0.75)
    be_quiet()
    sleep(0.75)
