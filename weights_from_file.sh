#!/bin/sh
#ll OS3E graphs:

C=1
EXT=pdf
# Add FORCE to forcibly regenerate metrics.
# Only needed when the data schema or set of input topos changes.
FORCE='-f'
BOOL=True
FILE=os3e

# Generate all latency metrics data for OS3E topology
TOPO=os3e,Geant2012,Grnet
./generate.py --topo_list ${TOPO} --weights_from_file ${BOOL} --weights_file ${FILE}  --from_start ${C} --all_metrics -w --write_dist  --write_combos -w -e ${EXT} ${FORCE}
