'''This script was found at https://github.com/brandonheller/ and was
edited by Spyridon Mastorakis.'''

import os

from lib.options import parse_args
import networkx as nx
# From http://hoegners.de/Maxi/geo/
import geo

# To test, go to http://www.daftlogic.com/projects-google-maps-distance-calculator.htm
# and run this code - see if the Portland - SanFran distance is ~533 miles.
# portland = geo.xyz(45.5, -122.67)
# sanfran = geo.xyz(37.777, -122.419)
METERS_TO_MILES = 0.000621371192
# print geo.distance(portland, sanfran) * METERS_TO_MILES

from os3e_weighted import OS3EWeightedGraph

mapping = {}

def has_weights(g):
    e1 = g.edges()[0]
    return 'weight' in g[e1[0]][e1[1]]

def total_weight(g):
    total = 0.0
    for src, dst in g.edges():
        total += g[src][dst]['weight']
    return total

def has_all_locs(g):
    for n in g.nodes():
        if 'Latitude' not in g.node[n] or 'Longitude' not in g.node[n]:
            return False
    return True

def has_a_location(g):
    for n in g.nodes():
        if 'Latitude' in g.node[n] and 'Longitude' in g.node[n]:
            return True
    return False

def num_geo_locations(g):
    num_in = 0
    num_out = 0
    for n in g.nodes():
        if 'Latitude' in g.node[n] and 'Longitude' in g.node[n]:
            num_in += 1
        else:
            num_out += 1
    return num_in, num_out

def lat_long_pair(node):
    return (float(node["Latitude"]), float(node["Longitude"]))


def dist_in_miles(g, src, dst):
    '''Given a NetworkX graph data and node names, compute mileage between.'''
    src_pair = lat_long_pair(g.node[src])
    src_loc = geo.xyz(src_pair[0], src_pair[1])
    dst_pair = lat_long_pair(g.node[dst])
    dst_loc = geo.xyz(dst_pair[0], dst_pair[1])
    return geo.distance(src_loc, dst_loc) * METERS_TO_MILES


#The following are OK (disconnections indicated on the map):
#Bandcon: NY/NJ disconnected
#BtLatinAmerica: hopelessly disconnected
#DialtelecomCz: some node junctions unclear
#Eunetworks: primary map shows one lone node (Duct-only market)
#Ntelos: OK, 47 is disconn (Washington DC).  Intentional: network partner.
#Ntt: OK, peering points shown.
#Oteglobe: OK, peering points shown.
#Telcove: OK, 62 (Hickory) /66 (Wilmington) disconn on map.
OK_DISCONN = ['Bandcon']
def ok_disconn(topo):
    '''Return True if topo is known to be disconnected, but OK.'''
    return topo in OK_DISCONN

#These seem like errors:
#** Dfn: node 30, WUP, is disconnected - should connect to DOR(29) and BIR(31).  30 to 31.
#Looking at the map (http://www-win.rrze.uni-erlangen.de/cgi-bin/ipqos/map.pl?config=win)
#** Evolink: 21 and 38 are disconnected?  doesn't look like it on the map.
#21: Sevlievo - should connect to Sofia.
#38: Instanbul virtual connection - off-site connection, OK
#** Globenet: 1 disconn comp, 13: Manaus, but Manaus is connected to Boa Vista (node 11.)
#** GtsCe: 149 (Bucuresti labeled 1) disconn, and only one node there.
#Brasov (90) and Constanta (94) should be connected, at least.
#Ploiesti should connect to the leftmost one, right?
#Would be nice to fix - a really interesting topology.
#PDF at: http://www.gtsce.com/file/en/maps/gts-ce-network.pdf
#Easier to grab details than the flash map.
#** HiberniaUs: 21 disconn - Internal 0
#Shouldn't there be a green link connecting 21 to Halifax?
#** KentmanApr2007: 11 (Medway ACL) is missing, yet it is connected to UoG-M - unclear at what speed.
#** Navigata: 1(Victoria) is disconn.
#source has died:
#http://www.navigata.ca/about-us/our-network/map_national_network.pdf
#new map at http://www.navigata.ca/about-us/network-map.aspx
#If you click on the map, it shows details for the area around Victoria, and how it connects to Vancouver.
#** Nsfcnet: 9 is disconn (CERNET).  Should connect to Tsinghua
#** Tw: 6 (Amarillo), 28 (Corpus Christi), 63(Greenville), 66(Spartanbug), 68(Charleston)
#http://www.twtelecom.com/about_us/networks.html
#Labels for greenville and Chattanooga are switched; Chattanooga is the disconnected one. 
#** Uninett: 23 (HiAK Kjeller), 45 (HSM Molde), 47 (HSM Kristiansun)
#23 (HiAK Kjeller) should connect to UNIK Kjeller in the bottom right
#45 (HSM Molde) should connect to HiA Alesund and HSM Kristian-sund
#47 (HSM Kristiansun) should connect to HSM Molde and Uninett Teknobyen
#** UsSignal: 6(Akron), 16(Evansville) disconn
#6(Akron) connects to Cleveland, Lima, and Youngstown
#16(Evansville) (OK, is disconn)
KNOWN_DISCONN_ERR = ["Dfn"]


#I'm not sure about the following; can someone take a look at these?
#** Bren: why are there so many nodes in the gml, but not the graph?
#** Colt: dashed lines and disconnections
#** DeutscheTelekom: many connections not shown
#** Garr199901: source field seems down.
#node 7 (EUMED CONNECT) is missing a connection and location, but not shown on the map.
#Source yields 404.  http://www.garr.it/reteGARR/mappa.php
#** Garr200212: component 14 is disconnected (EUMED connect)
#** other Garr* topos
#** Istar: 9 disconn: Hamilton, CA
#Why is the source MCI?  The link in the note field doesn't seem to connect to the topology either.
#** Padi: lots of disconn.
#padi2.ps domain appears dead:
#http://www.padi2.ps/maps.php
KNOWN_DISCONN_ERR += ['Bren']
def known_disconn(topo):
    '''Return True if topo is known to be errantly disconnected.'''
    return (topo in KNOWN_DISCONN_ERR) or 'Garr' not in topo

# Graphs for which we have multiple versions: only consider the latest ones.
OLD_VERSIONS = ['Arpanet']
NEWEST_VERSIONS = ['Geant2012']

def old_version(topo):
    '''Return True if topo is known to be an old version and should be ignored.''' 
    for old in OLD_VERSIONS:
        if old in topo:
            if topo in NEWEST_VERSIONS:
                return False
            else:
                return True            
    return False

BLACKLIST = [
    'Globalcenter',  # Full mesh != physical topo.
]
def blacklisted(topo):
    '''Return True if topo is in a blacklist.'''
    return topo in BLACKLIST


#No locations at all (node labels hard to read, imprecisely defined, or didn't get to)
KNOWN_NO_LOCATIONS_ERR = ['Ai3']
def known_no_loc(topo):
    return topo in KNOWN_NO_LOCATIONS_ERR


def node_is_internal(g, n):
    if 'Internal' not in g.node[n]:
        return True
    elif 'Internal' in g.node[n] and g.node[n]["Internal"] != 0:
        return True
    else:
        return False


def missing_locs_are_external(g):
    '''Return True if each node missing a location is external.'''
    for n in g.nodes():
        if ('Latitude' not in g.node[n] or
            'Longitude' not in g.node[n]):
            if node_is_internal(g, n):
                return False
    return True


def remove_external_nodes(g):
    for n in g.nodes():
        if not node_is_internal(g, n):
            print "removing node %s: %s" % (n, g.node[n])
            g.remove_node(n)


def attach_weights(g):
    for src, dst in g.edges():
        g[src][dst]["weight"] = dist_in_miles(g, src, dst)
            

def node_is_hyperedge(g, n):
    if 'hyperedge' in g.node[n] and g.node[n]['hyperedge'] == 1:
        return True
    else:
        return False


def missing_locs_are_hyperedges(g):
    '''Return True if each node missing a location is marked a hyperedge.'''
    for n in g.nodes():
        if ('Latitude' not in g.node[n] or
            'Longitude' not in g.node[n]):
            if not node_is_hyperedge(g, n):
                return False
    return True


def missing_locs_are_external_or_hyperedges(g):
    '''Return True if each node missing a location is marked a hyperedge
    or external
    '''
    for n in g.nodes():
        if ('Latitude' not in g.node[n] or
            'Longitude' not in g.node[n]):
            if not node_is_hyperedge(g, n) and node_is_internal(g, n):
                return False
    return True

'''Attach bandwidth weights to graph edges'''

def attach_bandwidth_weights(g):
	attr = nx.get_edge_attributes(g,'LinkLabel')
	for src,dst in g.edges():
		temp = str(attr[(src,dst)])
		if 'Gbps' or 'Gbit/s' in temp:
			factor=1
		elif 'Mbps' or 'Mbit/s' in temp:
			factor=1000
		space_found = False
		index = 0
		while not space_found:
			if temp[index]==' ':
				space_found=True
			else:
				index = index+1
		weight=''
		for i in range(index):
			weight = weight+temp[i]
		weight_num = float(weight)
		if factor!=1:
			weight_num = weight_num / factor
		g[src][dst]['weight'] = weight_num
		g[dst][src]['weight'] = weight_num
	return g


def import_zoo_graph(topo):
    '''Given name of Topology Zoo graph, return graph or error.
    
    @param g: NetworkX Graph
    @param usable: boolean: locations on all nodes and connected?
    @param note: error or note about mods
    '''
    filename = 'zoo/' + topo + '.gml'
    if not os.path.exists(filename):
        raise Exception("invalid topo path:%s" % filename)

    # Ignore old graphs
    if old_version(topo):
        return None, False, "Old version"
    if blacklisted(topo):
        return None, False, "Blacklisted topology"

    # Convert multigraphs to regular graphs; multiple edges don't affect
    # latency, but add complications when debugging.
    g = nx.Graph(nx.read_gml(filename,'UTF-8',True))
    cc = nx.connected_components(g)
    if len(cc) != 1:
        if ok_disconn(topo):
            # Remove disconnected components and continue
            # Do a pass to find the largest CC
            max_component_size = 0
            for comp in cc:
                if len(comp) >= max_component_size:
                    max_component_size = len(comp)
            # Do a pass to remove all nodes in non-largest CCs.
            for comp in cc:
                if len(comp) != max_component_size:
                    for n in comp:
                        g.remove_node(n)
        elif known_disconn(topo):
            return None, False, "Known disconnected topology"
        else:
            return None, False, "Unknown disconnected topology"
    cc = nx.connected_components(g)
    assert len(cc) == 1

    if not has_a_location(g):
        if known_no_loc(topo):
            return None, False, "Known no-weight topo"
        else:
            return None, False, "Unknown no-weight topo"

    if g.number_of_nodes() <= 9:
        print "********%s%s" % (topo, g.number_of_nodes())

    # Append weights
    if has_all_locs(g):
        options = parse_args()
        bandwidth = options.bandwidth
	if bandwidth:
		print("Weights used:Bandwidth")
		attach_bandwidth_weights(g)
	else:
		print("Weights used:Propagation delays")
        	attach_weights(g)
        #print "dist between %s and %s is %s" % (src, dst, g[src][dst]["weight"])    
        return g, True, None
    elif missing_locs_are_external(g):
        remove_external_nodes(g)
        attach_weights(g)
        return g, True, "OK - removed external nodes"
    elif missing_locs_are_hyperedges(g):
        return g, False, "OK - missing locs are only hyperedges"
    elif missing_locs_are_external_or_hyperedges(g):
        return g, False, "OK - missing locs are hyperedges or external"
    else:
        return g, False, "Missing location(s)"


def get_topo_graph(topo):
    if topo == 'os3e':
	g = OS3EWeightedGraph()
	return g, True, None
    elif topo == 'Geant2012':
        g, note, note2 = import_zoo_graph(topo)
	attr = nx.get_node_attributes(g,'Country')
	for node in g.nodes():
		temp = str(attr[node])
		mapping[node] = temp
	g = nx.relabel_nodes(g,mapping)
	return g, True, False 
    else:
	g, note, note2 = import_zoo_graph(topo)
        attr = nx.get_node_attributes(g,'label')
        for node in g.nodes():
                temp = str(attr[node])
                mapping[node] = temp
        g = nx.relabel_nodes(g,mapping)
        return g, True, False


		
