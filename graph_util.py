'''Functions for interconnecting two graphs with given interconnection points and generate the weights between these points. For future development regarding multi-domain environments'''

import json
import os
import math
import random
import string

import networkx as nx
import metrics
from zoo_tools import zoo_topos
from topo_lib import get_topo_graph, has_weights, dist_in_miles


'''Find connection points referring to this graph'''

def parse_points(g,dst,connection_points):
        counter = 1
        char = ''
        src= ''
        i=0
        enough = 0
        length= len(connection_points)
	while counter<length-1:
                enough=0
                while enough<1:
                        char = connection_points[counter]
                        if char == '@' and enough == 0:
                                char=' '
                                src = src + char
                                counter = counter +1
                        elif char!= ',' and char!=']' and enough == 0:
                                src = src + char
                                counter = counter +1
                        elif char == ',' and enough == 0:
                                enough = enough +1
                                counter = counter +1
                        else:
				enough = enough +1
                                counter = counter +1
                if enough == 1:
			if g.__contains__(src):
                        	dst.append(src)
			src=''
	return dst

'''Connect with an bidirectional edge the connection points given as arguments. Compute their weights , according to their distance '''

def connect_graphs(g):
	options = plot.parse_args()
	connection_points = []
	connection_points = options.connection_points
	counter = 1
	char = ''
	src= ''
	dst= ''
	enough = 0
	length= len(connection_points)
	while counter<length-1:
		enough=0
		while enough<2:
			char = connection_points[counter]
			if char == '@' and enough == 0:
				char=' '
				src = src + char
				counter = counter +1
			elif char == '@' and enough == 1:
				char=' '
                                dst = dst + char
                                counter = counter +1
			elif char!= ',' and char!=']' and enough == 0:
				src = src + char
				counter = counter +1
			elif char == ',' and enough == 0:
				enough = enough +1
				counter = counter +1
			elif char != ',' and char!=']' and enough == 1:
				dst = dst + char
				counter = counter +1
			else:
				enough = enough +1
				counter = counter +1
		if enough == 2:
                        print(src,dst)
                        g.add_edge(src, dst)
                        g.add_edge(dst, src)
                        g[src][dst]["weight"] = dist_in_miles(g, src, dst)
                        g[dst][src]["weight"] = dist_in_miles(g, dst, src)
			print(g[src][dst]["weight"])
			src= ''
			dst= ''	
	return g

'''Construct a table as a list with elements in the following format <switch-id>,<vlan tag>,<port>,<user>'''

def construct_array(g,mylist):
	for src,dst in g.edges():
		mylist.append((src,random.randint(1,4000),random.randint(1,48),str(''.join(random.choice(string.ascii_lowercase) for i in range(5)))))
	print mylist
	return mylist


