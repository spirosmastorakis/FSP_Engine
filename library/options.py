#!/usr/bin/env python
from optparse import OptionParser

# Weighted or not?
DEF_WEIGHTED = True

DEF_INPUT_DIR = 'data_out'
DEF_OUTPUT_DIR = DEF_INPUT_DIR

OPERATIONS = ['metrics', 'cdfs', 'ranges', 'pareto', 'cloud']
DEF_OPERATIONS = OPERATIONS

DEF_EXT = 'png'

DEF_TOPO = 'os3e'
TOPO_GROUPS = {
    'test1': ['Aarnet'],
    'test2': ['Aarnet', 'Abilene'],
    'test3': ['os3e', 'Geant2012']
}

DPI = 300

def parse_args2():
    opts = OptionParser()
    import sys


def parse_args():
    opts = OptionParser()
    print "entered arg parsing"
    import sys
    print sys.argv

    # Topology selection
    opts.add_option("--topo" , type = 'str', default = DEF_TOPO,
		    help = "only topology or whole(unified) topology")
    opts.add_option("--topo1", type = 'str', default = DEF_TOPO,
                    help = "first topology name")
    opts.add_option("--topo2", type = 'str', default = DEF_TOPO,
                    help = "second topology name")
    opts.add_option("--topo_group", type = 'str', default = None,
                    help = "topology group")
    opts.add_option("--topo_list", type = 'str', default = None,
                    help = "list of comma-separated topology names")
    opts.add_option("--topo_blacklist", type = 'str', default = None,
                    help = "list of comma-separated topologies to ignore")
    opts.add_option("--all_topos",  action = "store_true",
                    default = False,
                    help = "compute metric(s) for all topos?")
    
    opts.add_option("--connection_points" , type = "str", default = None,
		    help = "list of comma-separated connenction points.")
    	
    # Operations
    opts.add_option("--operation_list", type = 'string',
                    default = None,
                    help = "operations to show, from %s" % OPERATIONS)
    opts.add_option("--plot_list", type = 'string',
                    default = None, help = "plots to show")
    opts.add_option("--cdf_plot_list", type = 'string',
                    default = None, help = "CDF plots to show")
    opts.add_option("--gen_1ctrl_table",action = "store_true",
                    default = False, help = "generate LaTeX one-ctrl table?")
    
    # Shared output args
    opts.add_option("-w", "--write",  action = "store_true",
                    default = False,
                    help = "write plots, rather than display?")

    # Multiprocessing options
    opts.add_option("--no-multiprocess",  action = "store_false",
                    default = True, dest = 'multiprocess',
                    help = "don't use multiple processes?")
    opts.add_option("--processes", type = 'int', default = 8,
                    help = "worker pool size; must set multiprocess=True")
    opts.add_option("--chunksize", type = 'int', default = 50,
                    help = "batch size for parallel processing")

    # Metrics-specific arguments
    opts.add_option("--write_combos",  action = "store_true",
                    default = False,
                    help = "write out combinations?")
    opts.add_option("--write_dist",  action = "store_true",
                    default = False,
                    help = "write_distribution?")
    opts.add_option("--write_csv",  action = "store_true",
                    default = False,
                    help = "write csv file?")
    opts.add_option("--no-dist_only",  action = "store_false",
                    default = True, dest = 'dist_only',
                    help = "don't write out _only_ the full distribution (i.e.,"
                    "run all algorithms.)")
    opts.add_option("--weighted" , action = "store_true" , 
		    default = False , 
                    help = "graph weighted or not?")
    opts.add_option("--bandwidth" , action ="store_true",
		    default = False,
		    help="bandwidth as weights per edge?")
    
    opts.add_option("--use_prior",  action = "store_true",
                    default = False,
                    help =  "Pull in previously computed data, rather than recompute?")
    opts.add_option("--no-compute_start",  action = "store_false",
                    default = True, dest = 'compute_start',
                    help = "don't compute metrics from start?")
    opts.add_option("--no-compute_end",  action = "store_false",
                    default = True, dest = 'compute_end',
                    help = "don't compute metrics from end?")
    opts.add_option("--median",  action = "store_true",
                    default = False,
                    help = "compute median?")
    opts.add_option("-f", "--force", action = "store_true",
                    default = False,
                    help = "force operations to occur even if metrics are there")
    opts.add_option("--disjoint_paths", action = "store_true",
		    default = False, 
		    help = "disjoint path service or simple Shortest path")
    opts.add_option("--src", type = 'str',
                    default = None,
		    help = "src of disjoint paths")
    opts.add_option("--mix",type='str', 
		    default= None,
		    help = "mixture of tenant request")
    opts.add_option("--dst", type = 'str' , 
                    default = None,
		    help = "dst of disjoint paths")    
    opts.add_option("--reuse" , action = "store_true",
		    default = False,
		    help = "reusability computations")
    opts.add_option("--simple_paths" , type = 'int', 
		    default = None,
		    help = "number of simple paths, in which the reusability will be computed")
    opts.add_option("--disjoint" , type = 'int',
		    default = None,
		    help = "number of disjoint paths, in which the reusability will be computed")
    opts.add_option("--star_paths" , type = 'int',
	            default = None,
		    help = "number of star paths , in which the reusability will be measures")
    opts.add_option("--unbound" , type= 'int',
                    default = 0,
		    help = "ratio of unbound requests")

    opts.add_option("--weights_from_file" , action= "store_true",
		    default = False,
		    help = "read weights from .json file?")
    opts.add_option("--weights_file" , type = 'string',
		    default = None,
		    help = "name of .json file to read weights")

    # Plotting-specific input args
    opts.add_option("-i", "--input", type = 'string', 
                    default = None,
                    help = "name of input file")
    opts.add_option("--input_dir", type = 'string',
                    default = DEF_INPUT_DIR,
                    help = "name of input dir")
    opts.add_option("-o", "--output_dir", type = 'string',
                    default = DEF_OUTPUT_DIR,
                    help = "name of output file")
    

    options, arguments = opts.parse_args()
    
    if options.topo_group:
        if options.topo_group not in TOPO_GROUPS:
            	raise Exception("Invalid topo group specified: %s" % options.topo_group)
        options.topos = TOPO_GROUPS[options.topo_group]
    
    if options.topo != DEF_TOPO and options.topo_list:
        raise Exception("Both topo and topo_list provided; pick one please")
    else:
        if options.topo_list:
            	options.topos = options.topo_list.split(',')
        else:
            	options.topos = [options.topo]
    
    return options
