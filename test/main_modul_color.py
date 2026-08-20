import libs.modul_color_index as my_color 






def test_my_color():

    print("--- Start ---")

    my_color.color_setup()

    print("\n--- Test COLOR_OBJ ---")
    for i in range(len(my_color.color_index)):
        print(f"Index: {my_color.color_index[i].index}, R: {my_color.color_index[i].red}, G: {my_color.color_index[i].green}, B: {my_color.color_index[i].blue}, Brightness: {my_color.color_index[i].brightness}, RGB32: {hex(my_color.color_index[i].rgb32)}")
    
    print("\n--- Test int32_to_4bytes ---")
    for i in range(len(my_color.color_index)):
        b0, b1, b2, b3 = my_color.int32_to_4bytes(my_color.color_index[i].rgb32, little_endian=True)
        print(f"Index: {my_color.color_index[i].index}, RGB32: {hex(my_color.color_index[i].rgb32)}, Bytes: [{b0}, {b1}, {b2}, {b3}]")

    print("--- Ende ---")

def main():
    test_my_color()


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

