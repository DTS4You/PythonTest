import module_ws2812 as WS2812
import time

def mod_loader():
    print("Start-Loader")
    run_ws2812()


def run_ws2812():
    WS2812.test_function()



def main():
    mod_loader()


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
