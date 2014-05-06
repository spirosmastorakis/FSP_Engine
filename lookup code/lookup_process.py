'''Various functions for efficient lookup in tables'''

import json
import os
import math
import random
import string

import networkx as nx

import lib.plot as plot
import metrics
import plot_cdfs
import plot_ranges
import plot_cloud
import plot_pareto
#import map_combos
from zoo_tools import zoo_topos
from topo_lib import get_topo_graph, has_weights, dist_in_miles
import data_validation
import lookup
import kdtree
import init
import util_lookup


'''Validate the data generated'''
def init_lookup(mylist):
	num_rows = len(mylist)
	hash_value = [ [] for i in range(num_rows) ]
	data_validation.validation(mylist, hash_value, num_rows)

'''Read user's query for lookup'''
def read_query(query):
	print("Type the switch id - node name")
    	temp0 = str(raw_input())
	query.append(temp0)
   	print("Type the vlan-id")
    	temp1 = int(raw_input())
	query.append(temp1)
    	print("Type the port")
    	temp2 = int(raw_input())
	query.append(temp2)
    	print("Type the user-id")
    	temp3 = str(raw_input())
	query.append(temp3)
    	return query

'''Lookup process'''
def lookup_table(mylist,query):
	"""Tree structure is defined"""
	random.seed(1)
	P = lambda *coords: list(coords)
	tree = kdtree.Kd_tree([P(ord('a'),0,0,ord('a'))], kdtree.Orthotope(P(ord('a'),0,0,ord('a')),P(ord('z'),4000,48,ord('z'))))
	query_temp = []
	mylist_temp=[]
	hash1 = {}
	hash2 = {}
	crc32 = {}
	num_rows = len(mylist)
	query_size = len(query)
	found = lookup.linear_search(mylist,query,num_rows)
	init.precomputation_double_hashing(mylist,hash1,hash2,num_rows)
	lookup.open_addressing_with_double_hashing(mylist,query,hash1,hash2)
	init.precomputation_single_hashing(mylist,crc32,num_rows)
	lookup.single_hashing(mylist,query,crc32)
	util_lookup.copy_arrays(mylist,mylist_temp,num_rows)
	util_lookup.copy_arrays_1dim(query,query_temp,query_size)
	util_lookup.ascii_to_int(mylist_temp,query_temp,num_rows)
	tree = kdtree.Kd_tree(util_lookup.convert_to_acceptable_format(mylist_temp,num_rows), kdtree.Orthotope(P(ord('a'),0,0,ord('a')),P(ord('z'),4000,48,ord('z'))))
	kdtree.show_nearest(2, tree, P(query_temp[0],query_temp[1],query_temp[2],query_temp[3]))
	if found:
		print("-----Response to user's query: Could not allocate the requested resources, because there was a conflict----")
	else:
		mylist.append((query[0],query[1],query[2],query[3]))
		print("-----Respone to user's query: The requested resources were allocated successfully-----")
		print mylist
