#!/usr/bin/env python
'''Run FSP engine for one or more topos.'''
import json
import os

import networkx as nx
from lib.options import parse_args
import metrics
from zoo_tools import zoo_topos
from topo_lib import get_topo_graph, has_weights
from graph_util import connect_graphs,parse_points

if __name__ == "__main__":

    mylist = []
    global options
    options = parse_args()

    def do_all(name, g, i, t, data, mylist):
        global options
        assert options
        filename = ''
	stats, filename = metrics.do_metrics(options, name, g, mylist)
	
    if options.all_topos:
        topos = sorted(zoo_topos())
    else:
        topos = options.topos
    topo_test = nx.Graph()
    t = len(topos)
    ignored = []
    successes = []
    #g_unified = nx.Graph() #unified graph
    #g_unified = nx.union_all(topos) #unify all given graphs
   
    for i, topo in enumerate(topos):
        print "topo %s of %s: %s" % (i + 1, t, topo)
        g, usable, note = get_topo_graph(topo)
	    #g_unified = nx.union(g,topo_test)#unify graphs
        exp_filename = metrics.get_filename(topo, options)

        if not g:
            raise Exception("WTF?!  null graph: %s" % topo)
	
    
        elif not options.force and os.path.exists(exp_filename + '.json'):
            # Don't bother doing work if our metrics are already there.
            print "skipping already-analyzed topo: %s" % topo
            ignored.append(topo)
        elif not has_weights(g):
            ignored.append(topo)
            print "no weights for %s, skipping" % topo
        else:
            do_all(topo, g, 1, 1, None, mylist)
            successes.append(topo)

    print "successes: %s of %s: %s" % (len(successes), t, successes)
    print "ignored: %s of %s: %s" % (len(ignored), t, ignored)
