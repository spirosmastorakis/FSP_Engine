#!/bin/sh

C=1
EXT=pdf
# Add FORCE to forcibly regenerate metrics.
# Only needed when the data schema or set of input topos changes.
FORCE='-f'
WEIGHTED=True
#TOPO=Uunet,Geant2012,Ibm,Psinet,Rediris,Bbnplanet,Belnet2006,Ulaknet,CrlNetworkServices,Getnet
TOPO=os3e,Uunet,Geant2012,Ibm,Psinet,Rediris,Bbnplanet,Belnet2006,Ulaknet,CrlNetworkServices,Getnet #choose real network topologies from zoo
REUSE=True #computation of acceptance ratio and Flowspace rules
MIX='mix2' #choose mix of requests
#number and type of virtual network paths to associate with tenant requests
ITER=10 #number of simple paths
DIS=34 #number of sets of disjoint paths
STAR=50 #number of star topologies
UNBOUND=20 #percentage of unbound requests-->in this example we 20% of the total number of requests are unbound
POINTS=[United@Kingdom,HiNe@Nesna,NB@Mo@i@Rana,Hartford,New@York,Chicago,Navarra,Madrid,Bordeaux,Pau,Germany,Netherlands,Phoenix,Anaheim,Denizli,Usak,Palo@Alto,Tuckson,McLeanHouston,Miami,Jackson,Geel,Leuven] #future development for multi-domain environments
./generate.py --connection_points ${POINTS} --mix ${MIX} --topo_list ${TOPO} --reuse ${REUSE} --unbound ${UNBOUND} --star_paths ${STAR} --simple_paths ${ITER} --disjoint ${DIS} -w 

#BAND=True #graph weigths to represent link bandwidth (if it is available from zoo)---must include the argument bandwidth ${BAND} when running generate.py

#./generate.py --topo_list ${TOPO} --reuse ${REUSE} --bandwidth ${BAND} --star_paths ${STAR} --simple_paths ${ITER} --disjoint ${DIS} --connection_points ${POINTS}  -w