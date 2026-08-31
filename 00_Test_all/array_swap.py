import time

start = time.perf_counter()

array = [0,1,2,3,2,1,0,1,2,3,2,1,0,1,2,3,2,1,0,1,2,3,2,1]
#array = array * 10
color = [0,20,40,60,80,100,120]
print(array)

def color_to_array(arr, col):
    for i, val in enumerate(arr):
        if arr[i] < len(col):
            arr[i] = col[arr[i]]
        else:
            arr[i] = 0
    return arr

result_array = color_to_array(array, color)
print(result_array)

ende = time.perf_counter()
dauer = ende - start

print(f"Ausführungszeit: {dauer:.6f} Sekunden")