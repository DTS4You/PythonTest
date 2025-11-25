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


color_off       = (  0,  0,  0)
color_red       = ( 80,  0,  0)
color_green     = (  0, 80,  0)
color_blue      = (  0,  0, 80)
color_yellow    = ( 50, 50,  0)
color_default   = (  0,  0,  2)


strip[0].fill(color_red)
strip[1].fill(color_green)
strip[2].fill(color_blue)
strip[3].fill(color_yellow)
strip[4].set_pixel_line_gradient(0, 19, color_red, color_yellow)
strip[5].set_pixel_line_gradient(0, 19, color_yellow, color_blue)
strip[6].set_pixel_line_gradient(0, 19, color_blue, color_yellow)
strip[7].set_pixel_line_gradient(0, 19, color_yellow, color_red)

counter = numpix

def mask_stripe():
    global counter
    global numpix
    strip[4].set_pixel_line_gradient(0, 19, color_red, color_yellow)
    
    if counter > 0:
        strip[4].set_pixel_line(0, counter - 1 , color_default)
    if counter < numpix - 2:
        strip[4].set_pixel_line(counter + 3, numpix, color_default)
    if counter > 0:
        counter -= 1
    else:
        counter = numpix

while(True):
    
    #strip[3].rotate_right(1)
    #strip[4].rotate_left(1)

    mask_stripe()

    for i in range(8):
        strip[i].show()

    time.sleep(0.3)