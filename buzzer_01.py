from machine import Pin, PWM
import time

# Set GPIO pin for audio output
buzzer_1 = PWM(Pin(0))
buzzer_2 = PWM(Pin(1))

def play_tone(frequency):
    # Set maximum volume
    buzzer_1.duty_u16(1000)
    buzzer_2.duty_u16(1000)
    # Play tone
    buzzer_1.freq(frequency)
    buzzer_2.freq(frequency)

def be_quiet():
    # Set minimum volume
    buzzer_1.duty_u16(0)
    buzzer_2.duty_u16(0)

## Infinite loop
play_tone(200)
time.sleep(1)
be_quiet()
play_tone(60)
be_quiet()
time.sleep(1)

buzzer_1.deinit()
buzzer_2.deinit()


