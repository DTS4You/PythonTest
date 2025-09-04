######################################################
### Main-Program                                   ###
### Projekt: Bereich-Raumfahrt                     ###
### Version: 0.99                                  ###
### Datum  : 11.08.2025                            ###
######################################################
from machine import Pin, Timer                              # type: ignore
from libs.module_init import Global_Module as MyModule
import time                                                 # type: ignore


time_on    = 0.3
time_off   = 0.4
time_pause = 1.5

# ------------------------------------------------------------------------------
# --- Main Function                                                          ---
# ------------------------------------------------------------------------------
# 0 -> Spiegel -> Ring
# 1 -> Laser Sender
# 2 -> Laser Empfänger

def main():

    print("=== Start Main ===")
    

    MyWS2812.do_all_def()

    try:
        print("Start Main Loop")
 
        while (True):

            for i in range(0,2):                    # Laser
                MyWS2812.set_led_obj(6,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(6,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Boden 1
                MyWS2812.set_led_obj(0,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(0,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Spiegel / color_half
                MyWS2812.set_led_obj(5,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(5,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Empfänger
                MyWS2812.set_led_obj(7,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(7,"def")
                time.sleep(time_off)
            #----------------------------------------------------------
            for i in range(0,2):                    # Laser
                MyWS2812.set_led_obj(6,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(6,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Boden 2
                MyWS2812.set_led_obj(1,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(1,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Spiegel
                MyWS2812.set_led_obj(5,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(5,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Empfänger
                MyWS2812.set_led_obj(7,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(7,"def")
                time.sleep(time_off)
            #----------------------------------------------------------
            for i in range(0,2):                    # Laser
                MyWS2812.set_led_obj(6,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(6,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Boden 3
                MyWS2812.set_led_obj(2,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(2,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Spiegel
                MyWS2812.set_led_obj(5,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(5,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Empfänger
                MyWS2812.set_led_obj(7,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(7,"def")
                time.sleep(time_off)
            #----------------------------------------------------------
            for i in range(0,2):                    # Laser
                MyWS2812.set_led_obj(6,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(6,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Boden 4
                MyWS2812.set_led_obj(3,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(3,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Spiegel
                MyWS2812.set_led_obj(5,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(5,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Empfänger
                MyWS2812.set_led_obj(7,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(7,"def")
                time.sleep(time_off)
            #----------------------------------------------------------
            for i in range(0,2):                    # Laser
                MyWS2812.set_led_obj(6,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(6,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Boden 5
                MyWS2812.set_led_obj(4,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(4,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Spiegel
                MyWS2812.set_led_obj(5,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(5,"def")
                time.sleep(time_off)
            for i in range(0,2):                    # Empfänger
                MyWS2812.set_led_obj(7,"on")
                time.sleep(time_on)
                MyWS2812.set_led_obj(7,"def")
                time.sleep(time_off)
            #----------------------------------------------------------            

            time.sleep(time_pause)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        print("Exiting the program")
        MyWS2812.do_all_off()   

    print("=== End of Main ===")

# ==============================================================================
# ==============================================================================
    
# ###############################################################################
# ### Main                                                                    ###
# ###############################################################################


if __name__ == "__main__":

    if MyModule.inc_i2c:
        print("I2C_MCP23017 -> Load-Module")
        import libs.module_i2c as MyGPIO
        #print("I2C -> Setup")
        MyGPIO.i2c_setup()
        ### Test ###
        print("I2C -> SetOutput")
        MyGPIO.i2c_write(0,True)
        time.sleep(0.5)
        MyGPIO.i2c_write(0,False)

    if MyModule.inc_ws2812:
        print("WS2812 -> Load-Module")
        import libs.module_ws2812_v2 as MyWS2812         # Modul WS2812  -> WS2812-Ansteuerung
        #print("WS2812 -> Setup")
        MyWS2812.setup_ws2812()
        ### Test ###
        print("WS2812 -> Run self test")
        MyWS2812.self_test()
        print("WS2812 -> Blink Test")
        #MyWS2812.do_blink_test()
        #print("WS2812 -> Dot-Test")
        #MyWS2812.do_dot_test()

    if MyModule.inc_decoder:
        print("Decode -> Load-Module")
        import libs.module_decode as MyDecode
        #print("Decode -> Setup")
        MyDecode.decode_setup()
        ### Test ###
        #print("Decode -> Test")
        #MyDecode.decode_input("Test")

    if MyModule.inc_serial:
        print("Serial-COM -> Load-Module")
        import libs.module_serial as MySerial
        #print("Serial-Con -> Setup")
        MySerial.sercon_setup()
        ### Test ###
        #print("Serial-Con -> Test")
        #MySerial.sercon_write_out("Start Test")

    main()      # Start Main $$$

# Normal sollte das Programm hier nie ankommen !
print("___ End of Programm ___ -> = STOP =")

# ##############################################################################
