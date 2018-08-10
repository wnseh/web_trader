#!/usr/bin/env python3


def bubblesort(num_list):
    ret_list = num_list
    for x in range(len(ret_list)):
        for y in range(len(ret_list)-1):
            if ret_list[y] == 0:
                ret_list[y] = ret_list[y+1]
                ret_list[y+1] = 0
    return num_list





if __name__ == '__main__':
    y = [0,1,0,3,12]
    print(bubblesort(y))
