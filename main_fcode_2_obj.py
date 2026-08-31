def create_obj_array():
    global obj_array
    obj_array = [
        OBJECTS("H2Sat"         ,(1,2)),
        OBJECTS("EnMap"         ,(3,4)),
        OBJECTS("SARah"         ,(11, 12, 15)),
        OBJECTS("SAR_Lupe"      ,(3, 4)),
        OBJECTS("SATCOMBw"      ,(1, 2, 5, 6, 7, 8)),
        OBJECTS("TerraSAR-X"    ,(13, 14)),
        OBJECTS("SPOCK"         ,None),
        OBJECTS("Galileo"       ,(2, 3, 9, 10)),
        OBJECTS("Test_1"        ,(45))
]

class OBJECTS:
    def __init__(self, name, array):
        self.name       = name
        self.array      = array

create_obj_array()


def get_list_from_array(object_value):
    obj_value = []
    if isinstance(object_value, tuple):
        obj_value = list(object_value)
    if isinstance(object_value, int):
        obj_value = [object_value]
    if isinstance(object_value, type(None)):
        obj_value = []
    return obj_value


for obj in obj_array:
    print(get_list_from_array(obj.array))

print(get_list_from_array(obj_array[7].array))

