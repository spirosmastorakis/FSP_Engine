"""Hashing functions"""
import hashlib
"""Built in generators"""
import random
import string

"""In case of invalid data one of the two identical rows will be deleted and a new row will be generated at its place"""

def invalid_row_generation(mylist,i):
    mylist[i][1]= random.randint(1,4000)
    mylist[i][2]= random.randint(1,48)
    return mylist


"""Validity check. Check if each combination of [switch id, vland id, port] is unique,using a python build-in hash function"""

def validation(mylist, hash_value, num_rows):
    valid_data = 0
    while valid_data == 0:
        for rows in range(num_rows):
            hash_value[rows] = hashlib.md5('{}{}'.format(mylist[rows][1],mylist[rows][2])).hexdigest() #convert the integers to a string, because hashlib.md5 waits for a string argument
            #print hash_value[rows]
            """ Searching if there are two identical hash values"""
        for rows in range(num_rows):
            for i in range(rows+1,num_rows):
                if (hash_value[rows] == hash_value[i]):
                    print "Data validation failed as values of elements in rows %s and %s are identical. The row %s will be deleted , a row will be generated and the validity of the data will be checked again" % (rows,i,i)
                    invalid_row_generation(mylist,i)
        valid_data = 1 #the data generated was valid, so data validation can terminate
    print "Data validation completed successfully"
    return
