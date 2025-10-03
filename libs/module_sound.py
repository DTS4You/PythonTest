#------------------------------------------------------------------------------
# Sound     : Play Tone
# Version   : 1.00
#------------------------------------------------------------------------------

from machine import Pin, PWM
from utime import sleep

class PWM_SOUND:
    def __init__(self, PWN_PIN_1, PWN_PIN_2):
        self.speaker_1 = PWM(Pin(PWN_PIN_1))
        self.speaker_2 = PWM(Pin(PWN_PIN_2))
        self.time_red_1   = 0.3
        self.time_red_2   = 0.9
        self.time_green_1 = 0.2
        self.time_green_2 = 0.2
        self.time_off     = 0.1
        self.freq_red_1 = 200
        self.freq_red_2 = 100
        self.freq_green_1 = 1200
        self.freq_green_2 = 1200
 

    def play_tone(self, tone_frequency, tone_duration):
        self.speaker_1.duty_u16(1000)
        self.speaker_2.duty_u16(1000)
        self.speaker_1.freq(tone_frequency)
        self.speaker_2.freq(tone_frequency)
        sleep(tone_duration)

    def play_pause(self, pause_duration):
        self.speaker_1.duty_u16(0)
        self.speaker_2.duty_u16(0)
        sleep(pause_duration)

    def play_off(self):
        self.speaker_1.duty_u16(0)
        self.speaker_2.duty_u16(0)

    def play_sound(self, tone):
        if tone == "red":
            self.play_tone(self.freq_red_1, self.time_red_1)
            self.play_pause(self.time_off)
            self.play_tone(self.freq_red_2, self.time_red_2)
            self.play_off()
        if tone == "green":
            self.play_tone(self.freq_green_1, self.time_green_1)
            self.play_pause(self.time_off)
            self.play_tone(self.freq_green_2, self.time_green_2)
            self.play_off()

# -----------------------------------------------------------------------------
def main():

    print("=== Start Main -> Module_Sound ===")

    try:
        print("Start")
        
        pwm_sound = PWM_SOUND(0,1)

        pwm_sound.play_sound("red")
        sleep(0.5)
        pwm_sound.play_sound("green")

    except KeyboardInterrupt:
        print("Keyboard Interrupt")

    finally:
        print("Exiting the program")

    print("=== End Main ===")

# ------------------------------------------------------------------------------
# --- Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# =============================================================================


