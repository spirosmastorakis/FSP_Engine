"""generators for letters and integers"""
import random
import string
"""python built in hash functions"""
import zlib



"""Choose the number of rows to be generated"""

def read_rows(num_rows_list):
    print("Type the number of rows to be generated")
    num_rows_list[0] = int(raw_input())
    return num_rows_list

"""The first column refers to switch id, the second to vlan id, the third to port and the fourth to user id"""
"""Generate switch id as an integer in a range of 1-50, vlan id as an integer in a range of 0-4095, port as an integer
    in a range of 1-48 and user id as a single character"""

def array_creation(array,num_rows):
    for rows in range(num_rows):
        array[rows][0]=random.randint(1,50)
        array[rows][1]= random.randint(0,4095)
        array[rows][2]= random.randint(1,48)
        array[rows][3]= str(''.join(random.choice(string.ascii_lowercase) for i in range(5)))
    return

""""Read element for search"""

def read_element(element):
    print("Type the switch id")
    element[0] = int(raw_input())
    print("Type the vlan-id")
    element[1] = int(raw_input())
    print("Type the port")
    element[2] = int(raw_input())
    print("Type the user-id")
    element[3] = str(raw_input())
    return element

"""Precomputation for single hashing lookup"""

def precomputation_single_hashing(array,crc32_values,num_rows):
    for rows in range(num_rows):
        key = zlib.crc32('{}{}{}{}'.format(array[rows][0],array[rows][1],array[rows][2],array[rows][3]))
        crc32_values[key] = [ ('{}{}{}{}'.format(array[rows][0],array[rows][1],array[rows][2],array[rows][3])) ]
    return crc32_values


"""Precomputation for double hashing lookup according to the algorithm described in D.Knuth's - The Art of Computer Programming volume 3 section 6.4"""

def precomputation_double_hashing(array,hash1,hash2,num_rows):
    M=(2**32-1) #max value of integer in python
    for rows in range(num_rows):
        temp=""
	for char in array[rows][0]:
            temp = temp + str(ord(char))
        for column in range(1,3):
            temp = temp + str(array[rows][column])
        for char in array[rows][3]:
            temp = temp + str(ord(char))
        temp = string.atoi(temp)
        key1 = temp % M # h1(K) = K mod M
        key2 = 1 + (temp % (M-2)) # h2(K) = 1 + (K mod (M-2))
        hash1[key1] = [ ('{}{}{}{}'.format(array[rows][0],array[rows][1],array[rows][2],array[rows][3])) ]
        hash2[key2] = [ ('{}{}{}{}'.format(array[rows][0],array[rows][1],array[rows][2],array[rows][3])) ]
    return








