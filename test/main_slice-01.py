###############################################################################
### Name    : main_slice-01.py
###############################################################################
import time

def rotate_right(arr, n):
    n = n % len(arr)
    return arr[-n:] + arr[:-n]

def rotate_left(arr, n):
    n = n % len(arr)
    return arr[n:] + arr[:n]

array   = [0] * 20
pattern = [ 1, 2, 3, 2, 1]

array = pattern + array


for i in range(55):
    modulo = i % len(array)
    print(f"Step: {i:02d} | Modulo: {modulo:02d}", rotate_right(array, modulo)[len(pattern):])

    time.sleep(0.2)



