#!/bin/sh
# These instructions assume a raw Ubuntu 12.04.3 LTS server VM,
# but should work on any unix-ish system with sudo.

sudo apt-get install -y ssh git

echo "Installing setuptools"
sudo apt-get install -y python-setuptools

echo "Installing networkx, a Python library for graph manipulation."
sudo easy_install networkx

apt-get update

# Install topology zoo
sudo easy_install topzootools
sudo apt-get install unzip
wget http://topology-zoo.org/files/archive.zip
unzip archive.zip -d zoo

echo "Replace default zoo graphs with enchanced versions"
cp zoo_topos_enhancements/* zoo/

echo "\033[1m Here we go! Start the engine!"
./run_FSP_engine.sh
