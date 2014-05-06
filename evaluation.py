'''Computes acceptance ratio, number of non-overlapping flowspace rules and generates the non-overlapping flowspace rules for the domain-wide, the switch-wide and the port-wide slicing method. Simple paths, star topologies and sets of disjoint paths along with the network topology graph are needed for this computation.'''

from __future__ import division
import logging
import os
import time
import sys
import random
import math

import networkx as nx

from itertools import cycle, permutations
from file_libs import write_csv_file, write_json_file, read_json_file
from file_libs import write_dist_csv_file
from topo_lib import get_topo_graph
from lib.options import parse_args,parse_args2
import paths
from operator import itemgetter
import graph_util
from lib.graph import edge_disjoint,vertex_disjoint
#import lookup_process
import zlib

'''Precomputation of overall number of ports per graph node'''
def compute_overall_ports(g,overall_ports):
	for node in g:
		ports = g.neighbors(node)
		overall_ports[node]=ports
	return overall_ports

'''Precomputation for single hashing'''
def precomputation_single_hashing(array,crc32_values,num_rows):
    for rows in range(num_rows):
        key = zlib.crc32('{}'.format(array[rows]))
        crc32_values[key] = [ ('{}'.format(array[rows])) ]
    return crc32_values

'''Single hashing for lookup'''
def single_hashing(array,element,crc32_values):
    start = time.time() #start measuring the elapsed time
    key = zlib.crc32('{}'.format(element))
    key_existing = crc32_values.has_key(key) # check if the hashing key exists in the dictionary
    if key_existing :
        if crc32_values[key] == ['{}'.format(element)]:
            return True
    else:
        return False

def precomputation_single_hashing_2dim(array,crc32_values,num_rows):
    for rows in range(num_rows):
        key = zlib.crc32('{}{}'.format(array[rows][0],array[rows][1]))
        crc32_values[key] = [ ('{}{}'.format(array[rows][0],array[rows][1])) ]
    return crc32_values

'''Single hashing for lookup'''
def single_hashing_2dim(array,element,crc32_values):
    start = time.time() #start measuring the elapsed time
    key = zlib.crc32('{}{}'.format(element[0],element[1]))
    key_existing = crc32_values.has_key(key) # check if the hashing key exists in the dictionary
    if key_existing :
        if crc32_values[key] == ['{}{}'.format(element[0],element[1])]:
            return True
    else:
        return False

'''Find star subgraph of the original graph, by computing the degree of each node and for each degree found(i.e. degree = 1,2,3,4,...,max_value) until star_path_counter star paths are choosen'''

def choose_star_paths(g,star_paths,accepted_nodes,star_path_counter):
	degreedict = {}
	nodes = g.nodes()
	last_node = None
	degreedict = g.degree(g.nodes())
	flag = False
	numbers = []
	for i in range(star_path_counter):
		node = random.choice(nodes)
		temp = degreedict[node]
		accepted_nodes.append(node)
	for node in accepted_nodes:
		temp = []
		temp = g.neighbors(node)
		star_paths.append(temp)
	return star_paths,accepted_nodes
		


'''Main function to compute acceptance ratio and number of flowspace rules and generate the flowspace rules'''

def compute_metrics(FlowSpace_domain,FlowSpace_switch,FlowSpace_port,g,data,iters,dis_counter,dis_paths,star_path_counter,unbound_ratio):
	data['number of star paths'] = {}
	data['number of disjoint paths'] = {}
	data['number of simple paths'] = {}
	data['acceptance ratio domain-wide'] = {}
	data['acceptance ratio switch-wide'] = {}
	data['acceptance ratio port-wide']={}
	data['number of rules domain-wide'] = {}
	data['number of rules switch-wide'] = {}
	data['number of rules port-wide'] ={}
	counter = 0
	user_id = [0] # user_id number
	user_id.append(0)
	user_id.append(0)
	overall_ports= {} #storing the overall number of ports for each node
	accepted_perdomain = 0
	compute_overall_ports(g,overall_ports)
	accepted_perswitch = 0
	accepted_perswitch_perport = 0
        mylist_perdomain = []
	star_bound = math.trunc((100-unbound_ratio) * star_path_counter / 100)
	simple_bound = math.trunc((100-unbound_ratio) * iters / 100)
	disjoint_bound = math.trunc((100-unbound_ratio) * dis_counter / 100)
	mylist_perswitch = []
	mylist_perswitch_perport=[]
	show_vlan_unbound = [0]
	number_of_rules = [0] #number of rules
	number_of_rules.append(0)
	number_of_rules.append(0)	
	temp_rules = [0] #temporary number of rules
	temp_rules.append(0)
	temp_rules.append(0)
    #crc32_perdomain = {}
	#crc32_perswitch = {}
	#crc32_perswitch_perport = {}
	nodes = g.nodes()
	result_perdomain = False
	result_perswitch = False
	result_perswitch_perport = False
	precomputation_list = []
	star_paths = []
	precompute_ports(g,precomputation_list)
	accepted_nodes = []
	choose_star_paths(g,star_paths,accepted_nodes,star_path_counter)
	i=0		
	print("----Evaluation metrics will be computed in %d star paths,%d disjoint paths and %d simple paths" % (star_path_counter,dis_counter,iters))
	#temp_=0	
	'''Compute metrics using star topologies'''
	bound = True
	temp_counter = 0
	for paths in star_paths:
		#temp_ +=1
		if temp_counter<star_bound and bound==True:
			temp_counter +=1
		elif temp_counter==star_bound and bound==True:
			bound=False
		if bound:
			#print "bound"
			node = accepted_nodes[i]
			i=i+1
			vlan = random.randint(1,4095)
			result_perdomain = reusability_per_domain(FlowSpace_domain,user_id[0],mylist_perdomain,vlan,temp_rules)
                	result_perswitch = reusability_per_switch_star(precomputation_list,FlowSpace_switch,user_id[1],overall_ports,g,mylist_perswitch,vlan,paths,node,temp_rules)
                	result_perswitch_perport = reusability_perswitch_perport_star(FlowSpace_port,user_id[2],g,mylist_perswitch_perport,vlan,paths,node,precomputation_list,temp_rules)
		
		if not bound:
			#print "unbound"
			node = accepted_nodes[i]
			i=i+1
			result_perdomain = reusability_per_domain_unbound(FlowSpace_domain,user_id[0],mylist_perdomain,show_vlan_unbound,temp_rules)
                        result_perswitch = reusability_per_switch_star_unbound(precomputation_list,FlowSpace_switch,user_id[1],overall_ports,g,mylist_perswitch,paths,node,temp_rules)
                        result_perswitch_perport = reusability_perswitch_perport_star_unbound(FlowSpace_port,user_id[2],g,mylist_perswitch_perport,paths,node,precomputation_list,temp_rules)
                if result_perswitch_perport:
			user_id[2] += 1
  	       		accepted_perswitch_perport +=1
                if result_perdomain:
			user_id[0] += 1
     	               	accepted_perdomain = accepted_perdomain +1
                if result_perswitch:
			user_id[1] += 1
                       	accepted_perswitch = accepted_perswitch+1
		if result_perdomain and result_perswitch and result_perswitch_perport:
                                number_of_rules[0] += temp_rules[0]
                                number_of_rules[1] += temp_rules[1]
                                number_of_rules[2] += temp_rules[2]

		#print temp_
	'''Compute metrics using sets of disjoint paths'''
	new_disjoint_set = 0
	temp_counter = 0
	#temp_=0
	bound = True
	for paths in dis_paths:
		#temp_ +=1
		if temp_counter<disjoint_bound and bound==True:
                        temp_counter +=1
                elif temp_counter==disjoint_bound and bound==True:
                        bound=False
		if bound:
			#print "bound"
			if (new_disjoint_set % 2) == 0:
				vlan = random.randint(1,4095)#choose new vlan tag when a new set of disjoint paths is encountered
			new_disjoint_set = new_disjoint_set + 1
                	result_perdomain = reusability_per_domain(FlowSpace_domain,user_id[0],mylist_perdomain,vlan,temp_rules)
                	result_perswitch = reusability_per_switch(FlowSpace_switch,user_id[1],g,overall_ports,mylist_perswitch,vlan,paths,temp_rules)
                	result_perswitch_perport = reusability_perswitch_perport(FlowSpace_port,user_id[2],mylist_perswitch_perport,vlan,paths,precomputation_list,temp_rules)
                	if result_perswitch_perport:
				user_id[2] += 1
                		accepted_perswitch_perport +=1
                	if result_perdomain:
				user_id[0] += 1
                		accepted_perdomain = accepted_perdomain +1
                	if result_perswitch:
				user_id[1] += 1
                		accepted_perswitch = accepted_perswitch+1	
			if result_perdomain and result_perswitch and result_perswitch_perport:
                                number_of_rules[0] += temp_rules[0]
                                number_of_rules[1] += temp_rules[1]
                                number_of_rules[2] += temp_rules[2]

		if not bound:
			#print "unbound"
			result_perdomain = reusability_per_domain_unbound(FlowSpace_domain,user_id[0],mylist_perdomain,show_vlan_unbound,temp_rules)
                        result_perswitch = reusability_per_switch_unbound(FlowSpace_switch,user_id[1],g,overall_ports,mylist_perswitch,paths,temp_rules)
                        result_perswitch_perport = reusability_perswitch_perport_unbound(FlowSpace_port,user_id[2],mylist_perswitch_perport,paths,precomputation_list,temp_rules)
                        if result_perswitch_perport:
				user_id[2] += 1
                                accepted_perswitch_perport +=1
                        if result_perdomain:
				user_id[0] += 1
                                accepted_perdomain = accepted_perdomain +1
                        if result_perswitch:
				user_id[1] += 1
                                accepted_perswitch = accepted_perswitch+1
			if result_perdomain and result_perswitch and result_perswitch_perport:
                                number_of_rules[0] += temp_rules[0]
                                number_of_rules[1] += temp_rules[1]
                                number_of_rules[2] += temp_rules[2]

		#print temp_
	'''Compute metrics using simple paths'''

	temp_counter=0
	bound = True
	while counter < iters:
		src = random.choice(nodes)
                dst = random.choice(nodes)
                if src!=dst:
			i=0 	
			#choose the first randomly generated path
			for paths in nx.all_simple_paths(g,src,dst):
				i +=1
				if (i==1):
					break	
			if counter >= iters:
				break
			counter= counter +1
			if temp_counter<simple_bound and bound==True:
                        	temp_counter +=1
                	elif temp_counter==simple_bound and bound==True:
                        	bound=False		
			if bound:
				#print "bound"
				vlan = random.randint(1,4095)
				result_perdomain = reusability_per_domain(FlowSpace_domain,user_id[0],mylist_perdomain,vlan,temp_rules)
				result_perswitch = reusability_per_switch(FlowSpace_switch,user_id[1],g,overall_ports,mylist_perswitch,vlan,paths,temp_rules)
				result_perswitch_perport = reusability_perswitch_perport(FlowSpace_port,user_id[2],mylist_perswitch_perport,vlan,paths,precomputation_list,temp_rules)
			if not bound:
				result_perdomain = reusability_per_domain_unbound(FlowSpace_domain,user_id[0],mylist_perdomain,show_vlan_unbound,temp_rules)
                                result_perswitch = reusability_per_switch_unbound(FlowSpace_switch,user_id[1],g,overall_ports,mylist_perswitch,paths,temp_rules)
                                result_perswitch_perport = reusability_perswitch_perport_unbound(FlowSpace_port,user_id[2],mylist_perswitch_perport,paths,precomputation_list,temp_rules)
			if result_perswitch_perport:
				user_id[2] += 1
				accepted_perswitch_perport +=1
			if result_perdomain:
				user_id[0] += 1
				accepted_perdomain = accepted_perdomain +1
			if result_perswitch:
				user_id[1] += 1
				accepted_perswitch = accepted_perswitch+1 
			if result_perdomain and result_perswitch and result_perswitch_perport:
                               	number_of_rules[0] += temp_rules[0]
                               	number_of_rules[1] += temp_rules[1]
                               	number_of_rules[2] += temp_rules[2]

				#print counter

	data['number of star paths'] = star_path_counter
	data['number of disjoint paths'] = dis_counter
	data['number of simple paths'] = iters
	reusabil_perdomain = accepted_perdomain / (iters+dis_counter+star_path_counter)
        data['acceptance ratio domain-wide'] = float(reusabil_perdomain)
        print ("acceptance ratio domain-wide= %s" % reusabil_perdomain)
	reusabil_perswitch = accepted_perswitch / (iters+dis_counter+star_path_counter)
        data['acceptance ratio switch-wide'] = float(reusabil_perswitch)
        print ("acceptance ratio switch-wide= %s" % reusabil_perswitch)
	reusabil_perswitch_perport = accepted_perswitch_perport / (iters+dis_counter+star_path_counter)
        data['acceptance ratio port-wide'] = float(reusabil_perswitch_perport)
        print ("acceptance ratio port-wide= %s" % reusabil_perswitch_perport)
	data['number of rules domain-wide'] = number_of_rules[0]
	data['number of rules switch-wide'] = number_of_rules[1]
	data['number of rules port-wide'] = number_of_rules[2]
	print ("Number of rules for domain wide= %s" % number_of_rules[0])
	print ("Number of rules for switch wide= %s" % number_of_rules[1])
	print ("Number of rules for port wide= %s" % number_of_rules[2])			

'''Computation of acceptance ratio for the port-wide slicing method in star topologies. Each edge in star topologies has the format:
						
						neighbor
						^
                        |
						|
						|
                      neighbor <----center_of_star--->neighbor
						|
						|
						|
						neighbor

The topology will be converted to:

						neighbor_of_neighbor
						^
						|
						|
						|
						neighbor
                                                ^
                                                |
                                                |
                                                |
      neighbor_of_neighbor <---neighbor <----center_of_star--->neighbor--->neighbor_of_neighbor
                                                |
                                                |
                                                |
                                                neighbor
						|
						|
						|
						neighbor_of_neighbor
'''


def reusability_perswitch_perport_star(FlowSpace_port,user_id,g,mylist,vlan,paths,node,port_list,number_of_rules):
	query = []
        query2 = []
	rules_to_append = []
        f = itemgetter(0,1)
        length = len(paths)
	src_node = node
	temp_no =0
        for i in range(length):
                dst_node = paths[i]
                index = map(f,port_list).index((src_node,dst_node))
                port1 = port_list[index][2]
                index = map(f,port_list).index((dst_node,src_node))
                port2 = port_list[index][2]
                temp = (src_node,port1,dst_node,port2,vlan)
                query.append(temp)
                temp2 = (dst_node,port2,src_node,port1,vlan)
                query2.append(temp2)
		rules_to_append.append((user_id,3000,port1,src_node,vlan))
		rules_to_append.append((user_id,3000,port2,dst_node,vlan))
	'''convert star topology with one node in each radius into star topology with 2 nodes in each radius of the star topology'''
	for i in range(length):
		neighbor = paths[i]
		'''Compute number of FlowSpace rules for the center node'''
        	used_ports=len(g.neighbors(neighbor))
		temp_no += used_ports
		neighbors_of_neighbor = g.neighbors(neighbor)
		if len(neighbors_of_neighbor) == 1 and neighbors_of_neighbor[0] == src_node:
			continue
		found_neighbor_of_neighbor = False
		while not found_neighbor_of_neighbor:
			neighbor_of_neighbor = random.choice(neighbors_of_neighbor)
			if neighbor_of_neighbor != src_node:
				found_neighbor_of_neighbor = True
				temp_no += 2 #because of expansion to two nodes per star radius
		index = map(f,port_list).index((neighbor,neighbor_of_neighbor))
                port1 = port_list[index][2]
                index = map(f,port_list).index((neighbor_of_neighbor,neighbor))
                port2 = port_list[index][2]
		rules_to_append.append((user_id,3000,port1,neighbor,vlan))
		rules_to_append.append((user_id,3000,port2,neighbor_of_neighbor,vlan))
                temp = (neighbor,port1,neighbor_of_neighbor,port2,vlan)
                query.append(temp)
                temp2 = (neighbor_of_neighbor,port2,neighbor,port1,vlan)
                query2.append(temp2)	
        if len(mylist)==0:
                for i in range(len(query)):
                        temp1 = query[i]
                        temp2 = query2[i]
                        mylist.append(temp1)
                        mylist.append(temp2)
		user_id +=1
                for i in range(len(rules_to_append)):
                	FlowSpace_port.append(rules_to_append[i])
		number_of_rules[2] = temp_no
                return True
        for i in range(len(query)):
                temp1 = query[i]
                temp2 = query2[i]
                if ((temp1 in mylist) or (temp2 in mylist)):
                        return False
        for i in range(len(query)):
                temp1 = query[i]
                temp2 = query2[i]
                mylist.append(temp1)
                mylist.append(temp2)
	number_of_rules[2] = temp_no
	user_id += 1
	for i in range(len(rules_to_append)):
		FlowSpace_port.append(rules_to_append[i])
        return True

'''Computation of acceptance ratio for the port-wide slicing method in star topologies for unbound request.The topology will be converted to a star topology with 2 neighbors per radius exactly like above'''

def reusability_perswitch_perport_star_unbound(FlowSpace_port,user_id,g,mylist,paths,node,port_list,number_of_rules):
	vlan=0
	while vlan<=4096:
		rules_to_append=[]
		skip=False
		vlan +=1
		temp_no =0
        	query = []
        	query2 = []
        	f = itemgetter(0,1)
        	length = len(paths)
        	src_node = node
        	for i in range(length):
                	dst_node = paths[i]
                	index = map(f,port_list).index((src_node,dst_node))
                	port1 = port_list[index][2]
                	index = map(f,port_list).index((dst_node,src_node))
                	port2 = port_list[index][2]
                	temp = (src_node,port1,dst_node,port2,vlan)
			rules_to_append.append((user_id,3000,port1,src_node,vlan))
			rules_to_append.append((user_id,3000,port2,dst_node,vlan))
                	query.append(temp)
                	temp2 = (dst_node,port2,src_node,port1,vlan)
                	query2.append(temp2)
        	'''convert star topology with one node in each radius into star topology with 2 nodes in each radius of the star topology'''
        	for i in range(length):
               		neighbor = paths[i]
			used_ports=len(g.neighbors(neighbor))
                	temp_no += used_ports
                	neighbors_of_neighbor = g.neighbors(neighbor)
                	if len(neighbors_of_neighbor) == 1 and neighbors_of_neighbor[0] == src_node:
                	        continue
                	found_neighbor_of_neighbor = False
                	while not found_neighbor_of_neighbor:
                	        neighbor_of_neighbor = random.choice(neighbors_of_neighbor)
                	        if neighbor_of_neighbor != src_node:
					temp_no +=2
                	                found_neighbor_of_neighbor = True
                	index = map(f,port_list).index((neighbor,neighbor_of_neighbor))
                	port1 = port_list[index][2]
                	index = map(f,port_list).index((neighbor_of_neighbor,neighbor))
                	port2 = port_list[index][2]
                	temp = (neighbor,port1,neighbor_of_neighbor,port2,vlan)
                	query.append(temp)
			rules_to_append.append((user_id,3000,port1,neighbor,vlan))
			rules_to_append.append((user_id,3000,port2,neighbor_of_neighbor,vlan))
                	temp2 = (neighbor_of_neighbor,port2,neighbor,port1,vlan)
                	query2.append(temp2)
        	if len(mylist)==0:
                	for i in range(len(query)):
                	        temp1 = query[i]
                	        temp2 = query2[i]
                	        mylist.append(temp1)
                	        mylist.append(temp2)
			user_id +=1
               		for i in range(len(rules_to_append)):
                        	FlowSpace_port.append(rules_to_append[i])
			number_of_rules[2] = temp_no
                	return True
        	for i in range(len(query)):
        	        temp1 = query[i]
        	        temp2 = query2[i]
        	        if ((temp1 in mylist) or (temp2 in mylist)):
        	        	skip=True
                                break
                if skip:
                        continue
        	for i in range(len(query)):
        	        temp1 = query[i]
        	        temp2 = query2[i]
        	        mylist.append(temp1)
        	        mylist.append(temp2)
		number_of_rules[2] = temp_no
		user_id +=1
		for i in range(len(rules_to_append)):
			FlowSpace_port.append(rules_to_append[i])
        	return True
	return False

'''Computation of acceptance ratio for the switch-wide slicing method regarding star topologies. The topology will be converted to a star topology with 2 neighbors per radius exactly like above'''
def reusability_per_switch_star(port_list,FlowSpace_switch,user_id,overall_ports,g,mylist,vlan,paths,center_of_star,number_of_rules):
        query = []
	temp_no =0
	f = itemgetter(0,1)
	rules_to_append = []
        length = len(paths)
        for i in range(length):
                node = paths[i]
		if center_of_star!=node:
			used_ports = 1
			used_ports_neighbors = center_of_star
		else:
        		used_ports= len(paths)
			used_ports_neighbors = paths
        	unused_ports = len(overall_ports[node]) - used_ports
		unused_ports_neighbors = set(overall_ports[node]) - set(used_ports_neighbors)
        	if unused_ports < used_ports:
			for port in unused_ports_neighbors:
				rules_to_append.append((user_id,3000,port,node,vlan))
			rules_to_append.append((user_id,2000,'*',node,vlan))
        	        temp_no += unused_ports +1
        	elif used_ports < unused_ports:
        	        temp_no += used_ports
			for port in used_ports_neighbors:
                                rules_to_append.append((user_id,3000,port,node,vlan))
        	else:
        	        temp_no += math.trunc((used_ports+unused_ports)/2)
			for port in used_ports_neighbors:
                                rules_to_append.append((user_id,3000,port,node,vlan))   
		temp = (node,vlan)
                query.append(temp)
		if node!=center_of_star:
			neighbors_of_neighbor = g.neighbors(node)
			if len(neighbors_of_neighbor) == 1 and neighbors_of_neighbor[0] == center_of_star:
                        	continue
			found_neighbor_of_neighbor = False
                	while not found_neighbor_of_neighbor:
                		neighbor_of_neighbor = random.choice(neighbors_of_neighbor)
                        	if neighbor_of_neighbor != center_of_star:
                                	found_neighbor_of_neighbor = True
					temp_no += 2 #because of expansion to two nodes per star radius
					index = map(f,port_list).index((node,neighbor_of_neighbor))
                        		port1 = port_list[index][2]
                        		index = map(f,port_list).index((neighbor_of_neighbor,node))
                        		port2 = port_list[index][2]
					rules_to_append.append((user_id,3000,port1,node,vlan))
					rules_to_append.append((user_id,3000,port2,neighbor_of_neighbor,vlan))

			temp = (neighbor_of_neighbor,vlan)
			query.append(temp)
        if len(mylist) == 0:
                for element in range(len(query)):
                        temp = query[element]
                        mylist.append(temp)
		for i in range(len(rules_to_append)):
			FlowSpace_switch = rules_to_append[i]
		user_id +=1
                #precomputation_single_hashing_2dim(mylist,crc32,len(mylist))
		number_of_rules[1] = temp_no
                return True
        for element in range(len(query)):
                temp = query[element]
                #found = single_hashing_2dim(mylist,temp,crc32)
                if temp in mylist:
                #if found:
                        return False
        for element in range(len(query)):
                temp = query[element]
                mylist.append(temp)
        #precomputation_single_hashing_2dim(mylist,crc32,len(mylist))
	number_of_rules[1] = temp_no
	for i in range(len(rules_to_append)):
                        FlowSpace_switch = rules_to_append[i]
        user_id +=1
        return True

'''Computation of acceptance ratio for the switch-wide slicing method regarding star topologies(unbound request). The topology will be converted to a star topology with 2 neighbors per radius exactly like above'''
def reusability_per_switch_star_unbound(port_list,FlowSpace_switch,user_id,overall_ports,g,mylist,paths,center_of_star,number_of_rules):
	vlan=0
	while vlan<=4096:
		skip=False
		temp_no =0
		vlan+=1
		f = itemgetter(0,1)
		rules_to_append = []
        	query = []
        	length = len(paths)
        	for i in range(length):
			node = paths[i]
			if center_of_star!=node:
                        	used_ports = 1
                        	used_ports_neighbors = center_of_star
			else:
				used_ports_neighbors = g.neighbors(node)
                		used_ports=len(g.neighbors(node))
			unused_ports_neighbors = set(overall_ports[node]) - set(used_ports_neighbors)
                	unused_ports = len(overall_ports[node]) - used_ports
                	if unused_ports < used_ports:
				for port in unused_ports_neighbors:
                                	rules_to_append.append((user_id,3000,port,node,vlan))
                        	rules_to_append.append((user_id,2000,'*',node,vlan))
                        	temp_no += unused_ports +1
                
                	elif used_ports < unused_ports:
				for port in used_ports_neighbors:
                                	rules_to_append.append((user_id,3000,port,node,vlan))
                	        temp_no += used_ports
                	else:
				for port in used_ports_neighbors:
                                	rules_to_append.append((user_id,3000,port,node,vlan))
                	        temp_no += math.trunc((used_ports+unused_ports)/2)
        	        temp = (node,vlan)
                	query.append(temp)
                	if node!=center_of_star:
                	        neighbors_of_neighbor = g.neighbors(node)
                	        if len(neighbors_of_neighbor) == 1 and neighbors_of_neighbor[0] == center_of_star:
                	                continue
                	        found_neighbor_of_neighbor = False
                	        while not found_neighbor_of_neighbor:
                	                neighbor_of_neighbor = random.choice(neighbors_of_neighbor)
                	                if neighbor_of_neighbor != center_of_star:
                	                	temp_no += 2 #because of expansion to two nodes per star radius
						found_neighbor_of_neighbor = True						
						index = map(f,port_list).index((node,neighbor_of_neighbor))
                                        	port1 = port_list[index][2]
                                        	index = map(f,port_list).index((neighbor_of_neighbor,node))
                                        	port2 = port_list[index][2]
                                        	rules_to_append.append((user_id,3000,port1,node,vlan))
                                        	rules_to_append.append((user_id,3000,port2,neighbor_of_neighbor,vlan))
                	        temp = (neighbor_of_neighbor,vlan)
                	        query.append(temp)
        	if len(mylist) == 0:
        	        for element in range(len(query)):
        	                temp = query[element]
        	                mylist.append(temp)
			for i in range(len(rules_to_append)):
                        	FlowSpace_switch = rules_to_append[i]
        		user_id +=1
        	        #precomputation_single_hashing_2dim(mylist,crc32,len(mylist))
			number_of_rules[1] = temp_no
        	        return True
        		for element in range(len(query)):
        		        temp = query[element]
        		        #found = single_hashing_2dim(mylist,temp,crc32)
                	if temp in mylist:
                	#if found:
                		skip=True
                                break
                if skip:
                        continue
        	for element in range(len(query)):
        	        temp = query[element]
        	        mylist.append(temp)
        	#precomputation_single_hashing_2dim(mylist,crc32,len(mylist))
		number_of_rules[1] = temp_no
		for i in range(len(rules_to_append)):
                        FlowSpace_switch = rules_to_append[i]
        	user_id +=1
        	return True
	return False


'''Port precomputation based on the edges that are attached to each node'''			
def precompute_ports(g,mylist):
	for node in g.nodes():
		neighboors = g.neighbors(node)
		num_of_neigh = len(neighboors)
		for port in range(0,num_of_neigh):
			mylist.append((node,neighboors[port],port+1))
	return mylist	

'''Computation of acceptance ratio for the port-wide slicing method'''
def reusability_perswitch_perport(FlowSpace_port,user_id,mylist,vlan,paths,port_list,number_of_rules):
	query = []
	query2 = []
	f = itemgetter(0,1)
	temp_no=0
	rules_to_append = []
	length = len(paths)
	for i in range(length-1):
		temp_no += 2
                src_node = paths[i]
		dst_node = paths[i+1]
		index = map(f,port_list).index((src_node,dst_node))
		port1 = port_list[index][2]
		index = map(f,port_list).index((dst_node,src_node))
		port2 = port_list[index][2]
                temp = (src_node,port1,dst_node,port2,vlan)
		index = map(f,port_list).index((src_node,dst_node))
                rules_to_append.append((user_id,3000,port1,src_node,vlan))
		rules_to_append.append((user_id,3000,port2,dst_node,vlan))
                query.append(temp)
		temp2 = (dst_node,port2,src_node,port1,vlan)
		query2.append(temp2)
	rules_to_append.append((user_id,3000,port2,dst_node,vlan))
	temp_no +=1
	if len(mylist)==0:
		for i in range(len(query)):
			temp1 = query[i]
			temp2 = query2[i]
			mylist.append(temp1)
			mylist.append(temp2)
		for i in range(len(rules_to_append)):
			FlowSpace_port.append(rules_to_append[i])
		user_id +=1	
		number_of_rules[2] = temp_no
		return True
	for i in range(len(query)):
		temp1 = query[i]
		temp2 = query2[i]
		if ((temp1 in mylist) or (temp2 in mylist)):
			return False
	for i in range(len(query)):	
		temp1 = query[i]
                temp2 = query2[i]
		mylist.append(temp1)
		mylist.append(temp2)
	for i in range(len(rules_to_append)):
        	FlowSpace_port.append(rules_to_append[i])
        user_id +=1
	number_of_rules[2] = temp_no
	return True

'''Computation of acceptance ratio for the port-wide slicing method (unbound request)'''
def reusability_perswitch_perport_unbound(FlowSpace_port,user_id,mylist,paths,port_list,number_of_rules):
	vlan = 0
	while vlan<=4096:
		skip=False
		vlan+=1
		rules_to_append = []
		temp_no = 0
        	query = []
        	query2 = []
        	f = itemgetter(0,1)
        	length = len(paths)
        	for i in range(length-1):
			temp_no +=2
        	        src_node = paths[i]
        	        dst_node = paths[i+1]
        	        index = map(f,port_list).index((src_node,dst_node))
        	        port1 = port_list[index][2]
        	        index = map(f,port_list).index((dst_node,src_node))
        	        port2 = port_list[index][2]
        	        temp = (src_node,port1,dst_node,port2,vlan)	
			rules_to_append.append((user_id,3000,port1,src_node,vlan))
                	rules_to_append.append((user_id,3000,port2,dst_node,vlan))
        	        query.append(temp)
        	        temp2 = (dst_node,port2,src_node,port1,vlan)
        	        query2.append(temp2)
		rules_to_append.append((user_id,3000,port2,dst_node,vlan))
		temp_no +=1
        	if len(mylist)==0:
        	        for i in range(len(query)):
        	                temp1 = query[i]
        	                temp2 = query2[i]
        	                mylist.append(temp1)
        	                mylist.append(temp2)
			for i in range(len(rules_to_append)):
                		FlowSpace_port.append(rules_to_append[i])
        		user_id +=1
			number_of_rules[2] = temp_no
        	        return True
        	for i in range(len(query)):
        	        temp1 = query[i]
        	        temp2 = query2[i]
        	        if ((temp1 in mylist) or (temp2 in mylist)):
        	        	skip=True
                                break
                if skip:
                        continue
        	for i in range(len(query)):
        	        temp1 = query[i]
        	        temp2 = query2[i]
        	        mylist.append(temp1)
                	mylist.append(temp2)
		for i in range(len(rules_to_append)):
                	FlowSpace_port.append(rules_to_append[i])
        	user_id +=1
                number_of_rules[2] = temp_no
        	return True
	return False
		
'''Computation of acceptance ratio for the domain-wide slicing method'''

def reusability_per_domain(FlowSpace_domain,user_id,mylist,vlan,number_of_rules):
	length = len(mylist)
	rules_to_append = []
	if length == 0:
		FlowSpace_domain.append((user_id,3000,'*','*',vlan))
		user_id +=1
		mylist.append(vlan)
		#precomputation_single_hashing(mylist,crc32,1)
		return True
	else:
		#found = single_hashing(mylist,vlan,crc32)
		if not vlan in mylist:
			mylist.append(vlan)
			FlowSpace_domain.append((user_id,3000,'*','*',vlan))
                	user_id +=1
                       	#precomputation_single_hashing(mylist,crc32,len(mylist))
			number_of_rules[0] = 1
			return True
	return False
		
'''Computation of acceptance ratio for the domain-wide slicing method in case of an unbound request'''
					
def reusability_per_domain_unbound(FlowSpace_domain,user_id,mylist,show_vlan_unbound,number_of_rules):
	temp = show_vlan_unbound[0]+1
        while temp <= 4096:
		rules_to_append = []
       		#found = single_hashing(mylist,vlan,crc32)
        	if not temp in mylist:
 	       		mylist.append(temp)
			show_vlan_unbound[0]=temp
			number_of_rules[0] = 1
			FlowSpace_domain.append((user_id,3000,'*','*',show_vlan_unbound))
                	user_id +=1
			return True
		else:
			temp=temp+1
               #precomputation_single_hashing(mylist,crc32,len(mylist))
        return False




'''Computation of acceptance ratio for the switch-wide slicing method'''

def reusability_per_switch(FlowSpace_switch,user_id,g,overall_ports,mylist,vlan,paths,number_of_rules):
	query = []
	temp_no =0
	rules_to_append = []
	length = len(paths)		
	for i in range(length):
		node = paths[i]
		if i!=0 and i!=length-1:
			used_ports=2
			used_ports_neighbors = [paths[i-1],paths[i+1]]
		elif i==0:
			used_ports=1
			used_ports_neighbors = [paths[i+1]]
		else:
			used_ports=1
			used_ports_neighbors = [paths[i-1]]
                unused_ports = len(overall_ports[node]) - used_ports
		unused_ports_neighbors = set(overall_ports[node]) - set(used_ports_neighbors)
                if unused_ports < used_ports:      
			for port in unused_ports_neighbors:
                                rules_to_append.append((user_id,3000,port,node,vlan))
                        rules_to_append.append((user_id,2000,'*',node,vlan))
                	temp_no += unused_ports +1
                elif used_ports < unused_ports:
			for port in used_ports_neighbors:
				rules_to_append.append((user_id,3000,port,node,vlan))             
                        temp_no += used_ports
                else:
			for port in used_ports_neighbors:
                                rules_to_append.append((user_id,3000,port,node,vlan))                     
                        temp_no += math.trunc((used_ports+unused_ports)/2)
		temp = (node,vlan)
		query.append(temp)
	if len(mylist) == 0:
		for element in range(len(query)):
			temp = query[element]
        		mylist.append(temp)
		for i in range(len(rules_to_append)):
			FlowSpace_switch.append(rules_to_append[i])
		user_id += 1
        	#precomputation_single_hashing_2dim(mylist,crc32,len(mylist))
		number_of_rules[1] = temp_no
		return True
	for element in range(len(query)):
		temp = query[element]			
		#found = single_hashing_2dim(mylist,temp,crc32)
		if temp in mylist:
		#if found:
			return False
	for element in range(len(query)):
		temp = query[element]
		mylist.append(temp)
	for i in range(len(rules_to_append)):
                FlowSpace_switch.append(rules_to_append[i])
        user_id += 1
	#precomputation_single_hashing_2dim(mylist,crc32,len(mylist))
	number_of_rules[1] = temp_no
	return True

'''Computation of acceptance ratio for the switch-wide slicing method in case of an unbound request'''

def reusability_per_switch_unbound(FlowSpace_switch,user_id,g,overall_ports,mylist,paths,number_of_rules):
	vlan=0
	while vlan<=4096:
		skip=False
		rules_to_append= []
		temp_no= 0
		vlan+=1
        	query = []
        	length = len(paths)
        	for i in range(length):
			node = paths[i]
			if i!=0 and i!=length-1:
                        	used_ports=2
                        	used_ports_neighbors = [paths[i-1],paths[i+1]]
                	elif i==0:
                        	used_ports=1
                        	used_ports_neighbors = [paths[i+1]]
                	else:
                        	used_ports=1
                        	used_ports_neighbors = [paths[i-1]]
                	unused_ports = len(overall_ports[node]) - used_ports
                	unused_ports_neighbors = set(overall_ports[node]) - set(used_ports_neighbors)
                	if unused_ports < used_ports:
				for port in unused_ports_neighbors:
                                	rules_to_append.append((user_id,3000,port,node,vlan))
                        	rules_to_append.append((user_id,2000,'*',node,vlan))
                	        temp_no += unused_ports +1
                	elif used_ports < unused_ports:
				for port in used_ports_neighbors:
                                	rules_to_append.append((user_id,3000,port,node,vlan))
                	        temp_no += used_ports
                	else:
				for port in used_ports_neighbors:
                                	rules_to_append.append((user_id,3000,port,node,vlan))
                	        temp_no += math.trunc((used_ports+unused_ports)/2)
        	        temp = (node,vlan)
        	        query.append(temp)
        	if len(mylist) == 0:
        	        for element in range(len(query)):
        	                temp = query[element]
        	                mylist.append(temp)
			for i in range(len(rules_to_append)):
                		FlowSpace_switch.append(rules_to_append[i])
        		user_id += 1
        	        #precomputation_single_hashing_2dim(mylist,crc32,len(mylist))
			number_of_rules[1] = temp_no
        	        return True
        	for element in range(len(query)):
        	        temp = query[element]
        	        #found = single_hashing_2dim(mylist,temp,crc32)
        	        if temp in mylist:
        	        #if found:
        	                skip=True
				break
		if skip:
			continue
        	for element in range(len(query)):
        	        temp = query[element]
        	        mylist.append(temp)
        	#precomputation_single_hashing_2dim(mylist,crc32,len(mylist))
        	number_of_rules[1] = temp_no
		for i in range(len(rules_to_append)):
                	FlowSpace_switch.append(rules_to_append[i])
        	user_id += 1
        	return True
	return False
