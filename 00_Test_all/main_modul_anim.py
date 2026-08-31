import time

import libs.modul_anim_obj as my_anim 



def main():

    print("--- Start ---")

    my_anim.pattern_setup()
    my_anim.anim_setup()

    print("Objekte erzeugen")
    
    my_anim.anim_obj[1].modifyed = True

    print("Anzahl der Anim_Objekte:", len(my_anim.anim_obj))
    print(my_anim.anim_obj[0].pattern.lenght)
    print(my_anim.anim_obj[1].pattern.lenght)

    #for i in range(len(my_anim.anim_obj)):
    #    print("Objekt:", i ,"Array:", my_anim.anim_obj[i].led_array)

    print(my_anim.anim_obj[0].arr_lenght)

    for i in range(20):
        
        print(f"Objekt: {my_anim.anim_obj[0].position:02d} Array: {my_anim.anim_obj[0].do_anim_step()}")
        #print(f"Objekt: {my_anim.anim_obj[1].position:02d} Array: {my_anim.anim_obj[1].do_anim_step()}")

        time.sleep(0.2)
    

    print("--- Ende ---")
#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

