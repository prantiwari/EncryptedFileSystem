#!/bin/bash
# Setup script for EncrypFS
sudo apt-get install python-dev

# make private  
mkdir private
touch private/files.txt
chmod 700 private/files.txt

mkdir private/keys
chmod 700 private/keys
crypto="pycrypto-2.6.1"
# Compile the libraries
cd lib/$crypto
pwd
sudo python setup.py build
sudo python setup.py install

