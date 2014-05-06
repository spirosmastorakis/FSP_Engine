import math
"""Packagies for elapsed time measurement"""
import time
"""Import python built in hash functions"""
import zlib
import string

"""Import implemented modules"""
import init

"""Linear search with time performance measurement
    Time complexity O(N)
Returns True if found the requested element, otherwise returns False"""

def linear_search(array,element,num_rows):
    start = time.time() #start measuring the elapsed time
    for rows in range(num_rows):
        if ((element[0]==array[rows][0])and(element[1]==array[rows][1])and(element[2]==array[rows][2])and(element[3] == array[rows][3])):
            end=time.time() #stop measuring the elapsed time
            print("Linear search found the requested element in row %s after %s ms" % (rows,(end-start)*1000))
            return True
    end=time.time()
    print("Linear search did not find the requested element after %s ms of search" % ((end-start)*1000))
    return False

"""This algorithm may fail to find the requested element , even if it exists in the table, as it refers to the one dimensional lookup only. Instead of this algorithm the k-dimensional tree search algorithm(see kdtree.py) was implemented in order for the lookup function never to fail.
    
Binary Search with time performance measurement
It will not be implemented with recursion, due to Python Stack Overflow, but with iterations
The field according to which the array has been sorted can be selected. In this example, the array has been sorted according to the switch_id
Algorithm for binary search is described in D.Knuth's - The Art of Computer Programming volume 3 section 6.2.1 , Algorithm B


def binary_search(array_for_sorting,element):
    start = time.time() #start measuring the elapsed time
    starting_index = 0
    ending_index = len(array_for_sorting)
    while starting_index < ending_index :
        middle_value = (ending_index + starting_index) / 2
        if (array_for_sorting[middle_value][0] == element[0] and array_for_sorting[middle_value][1] == element[1] and array_for_sorting[middle_value][2] == element[2] and array_for_sorting[middle_value][3] == element[3]) :
            end=time.time() #stop measuring the elapsed time
            print("Binary search found the requested element in row %s after %s ms" % (middle_value,(end-start)*1000))
            return
        elif array_for_sorting[middle_value][0] > element[0] :
            ending_index=middle_value - 1
        else :
            starting_index = middle_value + 1
    end=time.time() #stop measuring the elapsed time
    print("Binary search did not find the requested element after %s ms" % ((end-start)*1000))
    return
"""

"""Open addressing search with double hashing"""
"""This algorithm is described in D.Knuth's - The Art of Computer Programming volume 3 section 6.4
Time complexity O(1)"""

def open_addressing_with_double_hashing(array,element,hash1,hash2):
    start = time.time() #start measuring the elapsed time
    M = (2**32-1)
    temp=""
    for char in element[0]:
        temp = temp + str(ord(char))
    for column in range(1,3):
        temp = temp + str(element[column])
    for char in element[3]:
        temp = temp + str(ord(char))
    temp = string.atoi(temp)
    """First hash key"""
    key1 = temp % M # h1(K) = K mod M
    """Second hash key"""
    key2 = 1 + (temp % (M-2)) # h2(K) = 1 + (K mod (M-2))
    key_existing = hash1.has_key(key1) # check if the first hashing key exists in the dictionary hash1
    if key_existing :
        if hash1[key1] == ['{}{}{}{}'.format(element[0],element[1],element[2],element[3])]:
            end=time.time() #stop measuring the elapsed time
            print("Open addressing search with double hashing found the requested element after %s ms" % ((end-start)*1000))
            return
    else:
        key1 = key1 - key2 #i <-- i - c
        if key1<0: # i < 0
            key1 = key1 + M # i <-- i + M
        key_prime_existing = hash2.has_key(key1) # check if the second hashing key exists in the dictionary hash2
        if key_prime_existing :
            if hash2[key1] == ['{}{}{}{}'.format(element[0],element[1],element[2],element[3])]:
                end=time.time() #stop measuring the elapsed time
                print("Open addressing search with double hashing found the requested element after %s ms" % ((end-start)*1000))
                return
    end=time.time() #stop measuring the elapsed time
    print("Open addressing search with double hashing did not find the requested element after %s ms" % ((end-start)*1000))
    return

"""Search with a single hashing
    Time complexity O(1)"""

def single_hashing(array,element,crc32_values):
    start = time.time() #start measuring the elapsed time
    key = zlib.crc32('{}{}{}{}'.format(element[0],element[1],element[2],element[3]))
    key_existing = crc32_values.has_key(key) # check if the second hashing key exists in the dictionary
    if key_existing :
        if crc32_values[key] == ['{}{}{}{}'.format(element[0],element[1],element[2],element[3])]:
            end=time.time() #stop measuring the elapsed time
            print("Simpe hashing found the requested element after %s ms" % ((end-start)*1000))
            return
    else:
        end=time.time() #stop measuring the elapsed time
        print("Simple hashing did not find the requested element after %s ms" % ((end-start)*1000))
        return





