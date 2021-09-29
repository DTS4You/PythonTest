import module_ws2812


def mod_loader():
    print("Start-Loader")
    run_led()


def init_led():
    module_ws2812.setup_ws2812()

def run_led():
    module_ws2812.run_ws2812()



def main():
    mod_loader()


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
