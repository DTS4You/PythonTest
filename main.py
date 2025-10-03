#
from machine import Pin, I2C # type: ignore
import mcp23017_raw
import time

i2c = I2C(0, scl=Pin(21), sda=Pin(20))
mcp = mcp23017_raw.MCP23017(i2c, 0x20)


while(True):

    input_reg = int.from_bytes(mcp._read(0x13, 1), 'big')
    mcp._write([0x12, input_reg])
    print(bin(input_reg))
    
    time.sleep(0.2)


