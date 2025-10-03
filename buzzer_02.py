#------------------------------------------------------------------------------
# Sound     : Play Tone
# Version   : 1.00
#------------------------------------------------------------------------------

from machine import Pin, PWM
from utime import sleep


SPEAKER_PIN_1 = 0
SPEAKER_PIN_2 = 1

speaker_1 = PWM(Pin(SPEAKER_PIN_1))
speaker_2 = PWM(Pin(SPEAKER_PIN_2))

ON_TIME_1   = 0.25
ON_TIME_2   = 0.5
OFF_TIME    = 0.1

FREQ_1 = 200
FREQ_2 = 100

def play_tone(tone_frequency, tone_duration):
    speaker_1.duty_u16(1000)
    speaker_2.duty_u16(1000)
    speaker_1.freq(tone_frequency)
    speaker_2.freq(tone_frequency)
    sleep(tone_duration)

def play_pause(pause_duration):
    speaker_1.duty_u16(0)
    speaker_2.duty_u16(0)
    sleep(pause_duration)

def play_off():
    speaker_1.duty_u16(0)
    speaker_2.duty_u16(0)

def play_sound():
    play_tone(FREQ_1, ON_TIME_1)
    play_pause(OFF_TIME)
    play_tone(FREQ_2, ON_TIME_2)
    play_off()


play_sound()

