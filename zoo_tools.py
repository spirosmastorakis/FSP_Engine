#!/usr/bin/env python
import os

from topo_lib import get_topo_graph

ZOO_DIR = 'zoo'


def zoo_topos():
    files = os.listdir(ZOO_DIR)
    # Ignore files starting with a .
    topos = [d.split(".")[0] for d in files if d != "" and d[0] != '.' and 'cache' not in d and '.gml' in d]
    return topos


def for_each_zoo_topo(fcn, data, max_iters = None):
    '''Execute the specified function for each topology in the zoo'''
    # Extract to just names
    topos = zoo_topos()
    t = len(topos)
    for i, topo in enumerate(topos):
        if not max_iters == None and i >= max_iters:
            break
        g = get_topo_graph(topo)
        fcn(topo, g, i, t, data)