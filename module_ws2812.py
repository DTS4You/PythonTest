import time
from neopixel import Neopixel

numpix = 16
strip_1 = Neopixel(numpix, 0, 2, "GRB")
strip_2 = Neopixel(numpix, 1, 3, "GRB")

red = (255, 0, 0)
orange = (255, 165, 0)
yellow = (255, 150, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
indigo = (75, 0, 130)
violet = (138, 43, 226)
white = (255,255,255)
grey = (50,50,50)
black = (0,0,0)
colors_rgb = (red, white, red, green, blue, indigo, violet)

# same colors as normaln rgb, just 0 added at the end
colors_rgbw = [color+tuple([0]) for color in colors_rgb]
colors_rgbw.append((0, 0, 0, 255))

# uncomment colors_rgb if you have RGB strip
# colors = colors_rgb
colors = colors_rgbw

strip_1.brightness(20)
strip_2.brightness(50)

strip_2.set_pixel_line_gradient(0, 7, white, grey)
strip_2.set_pixel_line_gradient(8, 15, grey, white)


while True:
    for color in colors:
        for i in range(numpix):
            strip_1.set_pixel(i, color)
            strip_2.rotate_right(1)
            time.sleep(0.05)
            strip_1.show()
            strip_2.show()

# End