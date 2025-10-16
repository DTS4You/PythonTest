#!/usr/bin/python
import sys
import termios
import tty


inked_buffer = 1


def inky():
    fd=sys.stdin.fileno()
    remember_attributes=termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())
    character=sys.stdin.read(inked_buffer)
    termios.tcsetattr(fd,termios.TCSADRAIN, remember_attributes)
    return character
