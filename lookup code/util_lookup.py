import string


"""Dummy copy of an four dimensional array to another"""

def copy_arrays(array,array2,num_rows):
    for rows in range(num_rows):
	temp0 = array[rows][0]
	temp1 = array[rows][1]
	temp2 = array[rows][2]
	temp3 = array[rows][3]
    	array2.append((temp0,temp1,temp2,temp3))
    return array2

"""Dummy copy of an one dimensional array to another"""
def copy_arrays_1dim(array,array2,num_rows):
	for rows in range(num_rows):
		array2.append(array[rows])
	return array2

"""Convert Ascii string to integer,so as the fourth column of array and element to be acceptable argument for the kdtree structure"""

def ascii_to_int(array,element,num_rows):
    for rows in range(num_rows):
        i = array[rows][0]
        temp = ""
        for char in i:
            temp= temp+ str(ord(char))
        i=temp
        array[rows] = (string.atoi(i),array[rows][1],array[rows][2],array[rows][3])	
    for rows in range(num_rows):
        i = array[rows][3]
        temp = ""
        for char in i:
            temp= temp+ str(ord(char))
        i=temp
        array[rows] = (array[rows][0],array[rows][1],array[rows][2],string.atoi(i))
    for i in element[0],element[3]:
    	temp=""
    	for char in i:
        	temp= temp+ str(ord(char))
	if i==element[0]:
    		i=temp
    		element[0]= string.atoi(i)
	else:
		i=temp
		element[3] = string.atoi(i)
    return array, element

"""Dummy functions. Their purpose is to convert the elemenents of the array structure to an acceptable format in order to be given as arguments to the test.Kd_tree function"""

def points2(array,i):
    return[array[i][y] for y in range(4)]

def convert_to_acceptable_format(array,num_rows):
    return [points2(array,i) for i in range(num_rows)]
