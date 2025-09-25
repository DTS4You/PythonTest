#
from machine import Pin, I2C # type: ignore
import mcp23017

i2c = I2C(0, scl=Pin(21), sda=Pin(20))
mcp = mcp23017.MCP23017(i2c, 0x20)


# property interface 8-bit
mcp.porta.mode = 0x00
#mcp.portb.mode = 0xff
mcp.porta.gpio = 0xAA
#mcp.portb.gpio = 0x02
