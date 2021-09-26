import machine
import uasyncio
import utime
import queue

# Settings
led = machine.Pin(25, machine.Pin.OUT)
btn = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

blink_state = False

# Coroutine: blink on a timer
async def blink(q):
    global blink_state

    blink_state = False
    delay_ms = 1000
    while True:
        if not q.empty():
            delay_ms = await q.get()
        blink_state = not blink_state
        print(blink_state)
        await uasyncio.sleep_ms(delay_ms)
        
# Coroutine: only return on button press
async def wait_button():
    btn_prev = btn.value()
    while (btn.value() == 1) or (btn.value() == btn_prev):
        btn_prev = btn.value()
        await uasyncio.sleep(0.04)
        
# Coroutine: entry point for asyncio program
async def main():
    
    # Queue for passing messages
    q = queue.Queue()
    
    # Start coroutine as a task and immediately return
    uasyncio.create_task(blink(q))
    
    # Main loop
    timestamp = utime.ticks_ms()
    while True:
        
        # Calculate time between button presses
        await wait_button()
        print("Press Button")
        new_time = utime.ticks_ms()
        delay_time = new_time - timestamp
        timestamp = new_time
        print(delay_time)
        
        # Send calculated time to blink task
        delay_time = min(delay_time, 2000)
        await q.put(delay_time)
    
# Start event loop and run entry point coroutine
uasyncio.run(main())