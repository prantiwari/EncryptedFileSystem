#!/bin/bash
# Setup script for EncrypFS
sudo apt-get install python-dev

# make private  
mkdir private
touch private/files.txt
chmod 700 private/files.txt

touch private/root_dir.cap
chmod 700 private/root_dir.cap

mkdir private/keys
chmod 700 private/keys
mkdir userdata/
crypto="pycrypto-2.6.1"
# Compile the libraries
cd lib/$crypto
pwd
sudo python setup.py build
sudo python setup.py install

# Setup the root_dir.cap
python client.py mkdir -r
