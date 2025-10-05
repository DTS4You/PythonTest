######################################################
### Main-Program                                   ###
### Projekt: Python Test                           ###
### Version: 0.99                                  ###
### Datum  : 11.08.2025                            ###
######################################################

from machine import Pin, PWM
import time # type: ignore


pwm=PWM(Pin(1), freq=1_000, duty_u16=65536//2)

time.sleep(3)

pwm.deinit()