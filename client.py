#!/usr/bin/env python
# Initial client version.
import httplib, urllib, getopt
import argparse
import crypto
import base64
import sys
import shlex
import os
from os import curdir
from os.path import join as pjoin

# Helpers to encode and decode a string with base64
EncodeAES = lambda s: base64.b64encode(s) 
DecodeAES = lambda e: base64.b64decode(e)
SPLIT_SYMBOL = "{}{}"
def get_handler(arg):
    with open('private/files.txt', "r") as f:
        for line in f:
            ind = line.find(arg.name)
            # here assumes the files have different names
            # TODO check for the same names that are substring of the other
            if ind != -1:
                key_ind = line.find("|")+1
                hash_ind = line.rfind("|")
                end_ind = line.find("\n") 
                cap = (line[key_ind:hash_ind], line[hash_ind+1:end_ind])
                break
    public = None
    file_name = arg.name
    abs_path = os.path.abspath(pjoin('private/keys/', file_name))
    # check if this file was created by the user
    if os.path.exists(abs_path):
        with open('private/keys/'+arg.name+"public", "r") as f:
            public = f.read() 
    with open('private/keys/'+arg.name+"private", "r") as f:
        private = f.read() 
    uri = cap[0]+":"+cap[1]
    # access the file via the write-cap
    cipher = get_data(uri) 
    data_ar = cipher.split(SPLIT_SYMBOL)
    sign = data_ar[1]
    data = data_ar[0]
    public = data_ar[2]
    assert(data_ar[3] == crypto.my_hash(public))

    valid = crypto.verify_RSA(public, sign, data)
    print "Valid: ", valid
    if valid:
        # generate the AES decryption key and decrypt
        salt = "a"*16
        s = str(cap[0] + salt)
        hashed_key = crypto.my_hash(s)
        ptext = crypto.decrypt(data, hashed_key[:16])   
        txt = ptext.find(SPLIT_SYMBOL)
        print "Decrypted file is: ", ptext[:txt]

def get_data(name):
    conn = httplib.HTTPConnection("localhost:8000")
    conn.request("GET", "/"+name)
    r1 = conn.getresponse()
    print r1.status, r1.reason
    # Parse the http responce
    html = r1.read()
    data_ind = html.find("data=")
    html = html[data_ind+5:]
    data_end = html.find("<")
    data = html[:data_end]
    data = urllib.unquote(data).decode("utf8")
    data = DecodeAES(data)
    conn.close()
    return data
    
def put_handler(arg):
    #(cap, data) = crypto.encrypt(arg.data)
    # here cap is (my_hash(private_key), my_hash(public_key))
    (private, public, cap) = crypto.generate_RSA()
    # store the encrypted private key in the data
    # so that upon later updates authorized users can access it
    data = arg.data + SPLIT_SYMBOL + crypto.encrypt(private, cap[0], False)
    # use the read key as an encryption key for the concatted data
    salt = "a"*16
    s = str(cap[0] + salt)
    hashed_key = crypto.my_hash(s)
    # encrypt the data
    data = crypto.encrypt(data, hashed_key[:16], False)
    # sign it with private key
    signature = crypto.sign_data(private, data)
    # FINAL DATA IS
    # enc_data | signature | public_key | hash(public_key)
    data = data +SPLIT_SYMBOL+ signature + SPLIT_SYMBOL + public + SPLIT_SYMBOL + crypto.my_hash(public)

    # save the cap in a private file 
    with open('private/files.txt', "a") as f:
        c = arg.name+ "|" + cap[0] + "|" + cap[1] + "\n"
        f.write(c)
    # save the private key in a file 
    with open('private/keys/'+arg.name+"public", "w") as f:
        f.write(public)
    with open('private/keys/'+arg.name+"private", "w") as f:
        f.write(private)
    # double hash the key to get the file name
    file_name = crypto.my_hash(crypto.my_hash(cap[0]))
    print "Write cap for the file is: %s: %s" %( cap[0], cap[1])
    print "You can access the capability in private/files.txt"
    post_data(data, cap[0] + ":" + cap[1])  

def post_data(data, name):
    encoded = EncodeAES(data)
    params = urllib.urlencode({'data': encoded})
    headers = {"Content-type": "text/html/plain",
    "Accept": "text/plain"}
    conn = httplib.HTTPConnection("localhost:8000")
    conn.request("POST", "/"+ name, params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    conn.close()
def usage():
    print ' -------------------------------------------------------------------------'
    print ' MIT 6.854 Final project, 2013'
    print ' Team: ulziibay, joor2992,  otitochi @ mit.edu'
    print ' '
    print ' This is EncrypFS file system'
    print ' '
    print ' Usage:'
    print ' client.py --h'
    print ' client.py --g my_name.txt'
    print ' client.py --p my_name.txt "THIS IS A TEST DATA"'
    print ' '
    print ' --g Get the file with the name'
    print ' --p  Put the file and data'
    print ' -------------------------------------------------------------------------'
    sys.exit(' ')

def build_parser(parser, shellflag = False):
    subparsers = parser.add_subparsers(help='Program mode (e.g. Put or Get a file, etc.)', dest='mode')
    get_parser = subparsers.add_parser('get', help='Choose whether to get or put a file')
    get_parser.add_argument('-n',
                            '--name',
                            required=True,
                            help='Get a file with name')
    put_parser = subparsers.add_parser('put', help='Put a file')
    put_parser.add_argument('-n',
                            '--name',
                            required=True,
                            help='Put a file with name')
    put_parser.add_argument('-d',
                            '--data',
                            required=True,
                            help='Specify file content')
    if shellflag:
        shell_parser = subparsers.add_parser('shell', help='start shell')
        
def main():

    parser = argparse.ArgumentParser(description='Run EncrypFS client')
    build_parser(parser, True)
    args = parser.parse_args()
    print '\n\n'
    if args.mode == "get":
        get_handler(args)
    elif args.mode == "put":
        put_handler(args)
    elif args.mode == "shell":
        print "STARTING SHELL"
        shell()
    else:
        usage()

def shell():
    parser = argparse.ArgumentParser(prog='', description='Run EncrypFS client')
    build_parser(parser)
    while True:
        inp = raw_input("EncryptFS : ")
        try: 
            args = parser.parse_args(shlex.split(inp))

        #hack to stop parser from terminating program
        except SystemExit as e:
            continue

        if args.mode == "get":
            get_handler(args)
        elif args.mode == "put":
            put_handler(args)
        elif args.mode == "ls":
            continue
        elif args.mode == "mkdir":
            continue
        elif args.mode == "cd":
            continue
        else:
            usage()

if __name__ == '__main__':
    main()
