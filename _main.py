# Main Program
import machine
import uasyncio
#import utime
import module_ws2812
import time

# Settings
#led = machine.Pin(25, machine.Pin.OUT)
btn = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

blink_state = False
flash_state = False
stripe_refresh = False

def output_test():
    #print("1 -> " + str(blink_state))
    if blink_state:
        module_ws2812.do_test_on()
        module_ws2812.do_refresh()
    else:
        module_ws2812.do_test_off()
        module_ws2812.do_refresh()


def output_flash():
    #print("2 -> " + str(flash_state))
    if flash_state:
        module_ws2812.do_test_on()
    else:
        module_ws2812.do_test_off()

# Coroutine: blink on a timer
async def blink(delay):
    global blink_state
    delay_ms = 300
    while True:
        #print("Blink")
        blink_state = not blink_state
        output_test()
        await uasyncio.sleep_ms(delay_ms)
        
async def flash(delay):
    global flash_state
    delay_ms = 400
    while True:
        #print("Flash")
        flash_state = not flash_state
        #output_flash()
        await uasyncio.sleep_ms(delay_ms)

# Coroutine: only return on button press
async def wait_button():
    btn_prev = btn.value()
    while (btn.value() == 1) or (btn.value() == btn_prev):
        btn_prev = btn.value()
        await uasyncio.sleep(0.04)

############################################################################### 
### Main Program
###############################################################################
async def main():

    module_ws2812.setup_ws2812()
    
    # Queue for passing messages
    # q = queue.Queue()
    
    # Start coroutine as a task and immediately return
    print("Start Blink")
    uasyncio.create_task(blink(1000))
    
    print("Start Flash")
    uasyncio.create_task(flash(300))
    
    output_test()
    output_flash()
    
    ###########################################################################
    # Main loop
    ###########################################################################
    while True:
        
        await wait_button()
        print("Loop++++++++++++++++++++++++++++++++++++++")
        
    
# Start event loop and run entry point coroutine
uasyncio.run(main())