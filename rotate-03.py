
def rotate_right(l, n):
    return l[-n:] + l[:-n]

def rotate_left(l , n):
    return l[n:] + l[:n]

my_list = [1, 5, 10, 15, 20, 25, 30]

n = 0

sub_s = 2
sub_e = 5
for i in range(20):

    #new_list = my_list[:sub_s] + my_list[sub_e:]
    my_list = my_list[:sub_s] + rotate_right(my_list[sub_s:sub_e],1) + my_list[sub_e:]
    print(my_list)

