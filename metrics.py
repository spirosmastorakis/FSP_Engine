#!/usr/bin/env python
'''Compute evaluation metrics for the given topologies and tenant requests using the FSP engine
'''
import logging
import os
import time
import sys

import networkx as nx

from itertools import cycle
from file_libs import  write_json_file, read_json_file
from topo_lib import get_topo_graph
from lib.options import parse_args,parse_args2
import paths
from operator import itemgetter
import graph_util
from lib.graph import edge_disjoint,vertex_disjoint
#import lookup_process
import evaluation

logging.basicConfig(level=logging.DEBUG)

'''Get filename for acceptance ratio'''

def get_filename(topo, options):
    number_of_requests = options.star_paths + options.disjoint + options.simple_paths
    type_of_requests = options.unbound #bound or unbound?
    mix = options.mix
    filename = "acceptance_ratio/" + topo + str(number_of_requests) + mix  + "("+ str(type_of_requests) +"% unbound)" +"/"
    return filename

'''Get filename for FlowSpace tables'''

def get_tablefilename(topo,options):
    	number_of_requests = options.star_paths + options.disjoint + options.simple_paths
   	type_of_requests = options.unbound #bound or unbound?
    	mix = options.mix
	filename_domain = "tables/" + "domain-wide"  + topo + str(number_of_requests) + mix+ "(" + str(type_of_requests) + "% unbound)"+ "/"
	filename_switch = "tables/" + "switch-wide"  + topo + str(number_of_requests) + mix+ "(" + str(type_of_requests) + "% unbound)"+ "/"
	filename_port = "tables/" + "port-wide"  + topo + str(number_of_requests) + mix+ "(" + str(type_of_requests) + "% unbound)"+ "/"
	return filename_domain, filename_switch, filename_port

'''Get filename of inputing graph weigths. Used in cases of external weights'''

def get_filename_weights(options):
	filename = "weights/" + options.weights_file + ".json"
	return filename

'''Compute length of specific path'''

def get_length(apsp , path):
	length = len(path)
	total=0
	num = 0
	pathcycle = cycle(path)
	pathcycle2 = cycle(path)
	nextelem = pathcycle2.next()
	
	for i in pathcycle:
		if num < length-1:
			nextelem = pathcycle2.next()
			try:
				total +=  apsp[i][nextelem]
			except KeyError:
                        	return -1
			#print ("%s - %s = %s"  %(i,nextelem,apsp[i][nextelem]))
			num = num +1
		else:
			break
	#print total
	return total

'''Checks if the paths given are disjoint(except for a common source node and returns the two disjoint paths with the lowest weights'''

def get_disjoint(g,paths_temp):
	for i in range(len(paths_temp)):
		for y in range(i+1,len(paths_temp)):
			counter = 0
			vertices = set([])
			path1,cost1,dst1=paths_temp[i]
			path2,cost2,dst2=paths_temp[y]
			for vertex in path1:
				for node in path2:
					if vertex == node:
						counter = counter +1
						if counter > 1:
							break	
				if counter >1:
					break
			if counter <=1:
				return paths_temp[i],paths_temp[y]

	return None,None

'''Read weights from .json file'''

def read_weights_from_file(g,filename):
	weights = {}
	weights = read_json_file(filename)
	for src,dst in g.edges():
		tuples = [weights.get(src)]
		if tuples[0]!=None:
			try:
				index = tuples[0].index(dst)
			except ValueError:
				continue
			else:
				g[src][dst]['weight'] = tuples[0][index+1]
		tuples = [weights.get(dst)]
		if tuples[0]!=None:
                        try:
                               	index = tuples[0].index(src)   
		      	except ValueError:
				continue
                        g[src][dst]['weight'] = tuples[0][index+1]
	return 

'''Compute the metrics for a single topology ---> acceptance ratio, flowspace rules and number of flowspace rules'''

def do_metrics(options, topo, g, mylist):
    temp=[]
    FlowSpace_domain = [] #FlowSpace Rules Table for domain wide slicing
    FlowSpace_switch = [] #FlowSpace Rules Table for switch wide slicing
    FlowSpace_port = [] #FlowSpace Rules Table for port wide
    query = []
    dst = [] #stores connection points as  multiple destinations
    paths_temp = [ ]	#stores disjoint paths from src to connection points
    print "computing metricss for topo: %s" % topo
    options = parse_args()
    if options.weights_from_file:
	filename_weights = get_filename_weights(options)
	read_weights_from_file(g,filename_weights)
    #graph_util.construct_array(g,mylist) #testing elements-please ignore
    #lookup_process.init_lookup(mylist)
    #lookup_process.read_query(query)
    #lookup_process.lookup_table(mylist,query)
    filename = get_filename(topo, options)
    filename_domain, filename_switch, filename_port = get_tablefilename(topo,options)
    data = {}  # Data to be computed --> acceptance ratio, flowspace rules and number of flowspace rules
    bandwidth = options.bandwidth
    if bandwidth:
	data['Weights used'] = 'Bandwidth'
    else:
	data['Weighs used'] = 'Propagation delay'
    apsp = nx.all_pairs_dijkstra_path_length(g) # weight computation according to dijkstra algorithm
    apsp_paths = nx.all_pairs_dijkstra_path(g) # all pair of dijkstra paths
    if options.disjoint_paths:
	dst=[]
	paths_temp = []
	connection_points = []
	connection_points = options.connection_points #for future implementation of multi-domain environments
	if g.__contains__(options.src):
		src = options.src
	else:		
		src = options.dst
	graph_util.parse_points(g,dst,connection_points)
	#print dst
	counter=0
        '''Disjoint paths computation'''
        for i in range(len(dst)):
		#print apsp[src][dst]
		temp1,temp2  = paths.vertex_disjoint_shortest_pair(g, src, dst[i])
		if temp1!=None and temp2!=None:
			length1 = get_length(apsp,temp1)
			paths_temp.append((temp1,length1,dst[i]))
			length2 = get_length(apsp,temp2)
			paths_temp.append((temp2,length2,dst[i]))
			counter = counter+2
		elif temp1!=None and temp2==None:
			length = get_length(apsp,temp1)
			paths_temp.append((temp1,length,dst[i]))
			counter=counter+1
	if counter == 0 or counter==1:
		print "Could not find two or more paths to check if they are disjoint"
		print "The execution will know be stopped"
		raise SystemExit
	#print apsp[src][dst]
	paths_temp = sorted(paths_temp, key=itemgetter(1))
	path1,path2 = get_disjoint(g,paths_temp)
	if path1 == None or path2 == None:
		print("Could not establish a set of disjoint paths between the requsted source and destination nodes")
		print "The execution will now be stopped"
                raise SystemExit
	
	print path1,path2
	path_temp1 , cost1, dst1 = path1
	path_temp2 , cost2, dst2 = path2
	apsp[src][dst1] = cost1
	apsp_paths[src][dst1] = path_temp1
	apsp[src][dst2]=cost2
	apsp_paths[src][dst2]=path_temp2

    '''Precomputations for metrics computation'''
    
    if options.reuse:
	star_path_counter = options.star_paths
	iters = options.simple_paths
	disjoints = options.disjoint
	dis_counter = 0
	unbound_ratio = options.unbound
	dst=[]
	dis_paths = []
	paths_temp = []
	connection_points = []
        connection_points = options.connection_points
	graph_util.parse_points(g,dst,connection_points)
	for node in g.nodes():
		if dis_counter >= disjoints:
			break
		src = node
		counter = 0
		for i in range(len(dst)):
                	#print apsp[src][dst]
                	temp1,temp2  = paths.vertex_disjoint_shortest_pair(g, src, dst[i])
                	if temp1!=None and temp2!=None:
                        	length1 = get_length(apsp,temp1)
				if length1 == -1:
					break
                        	paths_temp.append((temp1,length1,dst[i]))
                        	length2 = get_length(apsp,temp2)
				if length2== -1:
					break
                        	paths_temp.append((temp2,length2,dst[i]))
                        	counter = counter+2
                	elif temp1!=None and temp2==None:
                        	length = get_length(apsp,temp1)
				if length == -1:
					break
                        	paths_temp.append((temp1,length,dst[i]))
                        	counter=counter+1
		if counter == 0 or counter==1:
			continue
		paths_temp = sorted(paths_temp, key=itemgetter(1))
        	path1,path2 = get_disjoint(g,paths_temp)
		if path1!=None and path2!=None:
			dis_counter = dis_counter +2
			dis_paths.append(path1[0])
			dis_paths.append(path2[0])

	if dis_counter == disjoints:
		print("-------Found %d disjoint paths" % dis_counter)
	else:
		print("-------Found %d disjoint paths out of %d that was requested" % (dis_counter,disjoints))
    	evaluation.compute_metrics(FlowSpace_domain,FlowSpace_switch,FlowSpace_port,g,data,iters,dis_counter,dis_paths,star_path_counter,unbound_ratio) #this function actually computes acceptance ratio and generate non-overlapping flowspace rules

        '''creation of file containing flowspace rules in /tables folder. One file is cretated for each slicing method'''
        
	dirname = os.path.dirname(filename_domain)
        if not os.path.exists(dirname):
     	   os.mkdir(dirname)
        write_json_file(filename_domain+"Flowspace table" , FlowSpace_domain)
	dirname = os.path.dirname(filename_switch)
        if not os.path.exists(dirname):
    	    os.mkdir(dirname)
        write_json_file(filename_switch+"Flowspace table", FlowSpace_switch)
	dirname = os.path.dirname(filename_port)
    	if not os.path.exists(dirname):
        	os.mkdir(dirname)
       	write_json_file(filename_port + "Flowspace table", FlowSpace_port)

    '''creation of file containing acceptance ratio results and number of flowspace rules for each slicing method in /acceptance_ratio folder'''

    if options.use_prior:
        data = read_json_file(filename)
    else:
    	if options.write:
        	dirname = os.path.dirname(filename)
        	if not os.path.exists(dirname):
            		os.mkdir(dirname)
    			write_json_file(filename + 'acceptance_ratio', data)
       
    return data, filename

if __name__ == '__main__':
    options = parse_args()
    for topo in options.topos:
        g = get_topo_graph(topo)
        do_metrics(options, topo, g)
