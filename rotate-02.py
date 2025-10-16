def rotate_right(l, n):
    return l[-n:] + l[:-n]

def rotate_left(l , n):
    return l[n:] + l[:n]

my_list = [1, 5, 10, 15, 20, 25, 30]

n = 0

for i in range(20):

    my_list = rotate_left(my_list, 1)
    print(my_list)

