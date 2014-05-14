README - Flowspace Slicing Policy (FSP) Rule Engine v0.1

Overview
============

FSP Rule Engine is a Python implementation of three control plane slicing 
methods (domain-wide, switch-wide and port-wide slicing method) applicable to 
Software Defined Networking/OpenFlow environments. FSP Rule Engine takes 
as inputs real network topologies (parsed from the dataset of “The Internet 
Topology Zoo” project) and tenant requests for virtual network topologies (of 
three different types; point-to-point paths, star topologies and
disjoint path sets) across the given real network topologies. It computes the 
acceptance ratio of the given requests and generates the required tables of non-overlapping flowspace rules, so that isolation policy among tenants is enforced. 
The generated rules can be injected into an OpenFlow proxy controller such as 
FlowVisor. 

Instructions
=============

1.Give read,write and execute permissions to the FSP directory using the
  following command: chmod -R 700 FSP

2.Run INSTALL.sh script. Everything will be installed automatically and the
  Flowspace Slicing Policy rule engine will start.

3.Edit and run run_FSP_engine.sh script to determine the preferable parameters
  and to start the engine respectively.

Misc
============

For any bugs, patches or suggestions for future development please contact
Spyridon (Spiros) Mastorakis  <spiros[dot]mastorakis[at]gmail[dot]com> 
or Christos Argyropoulos <cargious[at]netmode[dot]ntua[dot]gr>. 

Disclosure
============

Scripts geo.py, geocode.py, os3e_weighted.py were found at the following url: 
https://github.com/brandonheller/ 
