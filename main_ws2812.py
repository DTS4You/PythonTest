# Example showing use of HSV colors
import time
from libs.neopixel import Neopixel


transfer_mode = "PUT"
numpix = 300

strip_1 = Neopixel(numpix, 0, 2, "GRB", 0.0001, transfer_mode)
strip_2 = Neopixel(numpix, 1, 3, "GRB", 0.0001, transfer_mode)
strip_3 = Neopixel(numpix, 2, 4, "GRB", 0.0001, transfer_mode)
strip_4 = Neopixel(numpix, 3, 5, "GRB", 0.0001, transfer_mode)


color_1 = (100,0,0)
color_2 = (0,100,0)
color_3 = (0,0,100)
color_4 = (50,40,70)
strip_1.fill(color_1)
strip_2.fill(color_2)
strip_3.fill(color_3)
strip_4.fill(color_4)

while(True):
    
    strip_1.show()
    strip_2.show()
    strip_3.show()
    strip_4.show()

    time.sleep(0.02)