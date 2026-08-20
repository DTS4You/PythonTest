###############################################################################
### Name    : main_slice-01.py
###############################################################################

array = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

# Print the entire array
print("Entire array:", array)

new_array = array[5:]  # Slicing from index 1 to 3 (4 is exclusive)
print("Sliced array (index 1 to 3):", new_array)


def rotate_right(arr, n):
    n = n % len(arr)
    return arr[-n:] + arr[:-n]

# Beispiel
daten = [1, 2, 3, 4, 5, 6, 7, 8]

rotiert = rotate_right(daten, 3)
print(rotiert)


def rotate_left(arr, n):
    n = n % len(arr)
    return arr[n:] + arr[:n]

# Beispiel
daten = [1, 2, 3, 4, 5, 6, 7, 8]

rotiert = rotate_left(daten, 3)
print(rotiert)
