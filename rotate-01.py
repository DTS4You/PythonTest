def rotate_right(l, n):
    return l[-n:] + l[:-n]

def rotate_left(l , n):
    return l[n:] + l[:n]

my_list = [1, 5, 10, 15, 20, 25, 30]

n = 0

for i in range(20):
    if i > len(my_list):
        n = i % len(my_list)
    else:
        n = i
    new_list = rotate_left(my_list, n)
    print(new_list)

