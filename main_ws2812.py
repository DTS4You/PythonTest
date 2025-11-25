# Example showing use of HSV colors
import time
from libs.neopixel import Neopixel


transfer_mode = "PUT"
numpix = 20

strip = []

strip.append(Neopixel(numpix, 0, 2, "GRB", 0.0001, transfer_mode))
strip.append(Neopixel(numpix, 1, 3, "GRB", 0.0001, transfer_mode))
strip.append(Neopixel(numpix, 2, 4, "GRB", 0.0001, transfer_mode))
strip.append(Neopixel(numpix, 3, 5, "GRB", 0.0001, transfer_mode))
strip.append(Neopixel(numpix, 4, 6, "GRB", 0.0001, transfer_mode))
strip.append(Neopixel(numpix, 5, 7, "GRB", 0.0001, transfer_mode))
strip.append(Neopixel(numpix, 6, 8, "GRB", 0.0001, transfer_mode))
strip.append(Neopixel(numpix, 7, 9, "GRB", 0.0001, transfer_mode))


color_1 = ( 50,0,0)
color_2 = (0, 50,0)
color_3 = (0,0, 50)
color_4 = (20,20,20)
strip[0].fill(color_1)
strip[1].fill(color_2)
strip[2].fill(color_3)
strip[3].fill(color_4)
strip[4].set_pixel_line_gradient(0, 19, color_1, color_2)
strip[5].fill(color_4)
strip[6].fill(color_4)
strip[7].fill(color_4)

strip[3].set_pixel(0, color_1)

while(True):
    
    strip[3].rotate_right(1)
    strip[4].rotate_left(1)

    for i in range(8):
        strip[i].show()

    time.sleep(0.3)