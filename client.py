#!/usr/bin/env python
# Initial client version.
import httplib, urllib, getopt
import argparse
import crypto
import base64
import sys
import shlex
import os
import subprocess
from os import curdir
from os.path import join as pjoin
from subprocess import call

# Helpers to encode and decode a string with base64
#HOST_IP = "54.201.152.172"
HOST_IP = "localhost"
PORT = "8080"
EncodeAES = lambda s: base64.b64encode(s) 
DecodeAES = lambda e: base64.b64decode(e)
SPLIT_SYMBOL = "{}{}"

# 4 different cap-s
# RO is for Read-Only
# WR is for Write/Read
FILE_READ_CAP = "FIL-RO"
FILE_WRITE_CAP = "FIL-WR"
DIR_READ_CAP = "DIR-RO"
DIR_READ_CAP = "DIR-WR"

def get_handler(arg):
    public = None
    uri = ""
    if arg.cap:
        uri = arg.cap
        cap = uri.split(":")
    else:
        # TODO this should read the current dir to find out the URI for the file
        with open('private/files.txt', "r") as f:
            for line in f:
                ind = line.find(arg.name)
                # here assumes the files have different names
                # TODO check for the same names that are substring of the other
                if ind != -1:
                    key_ind = line.find("|")+1
                    line = line[key_ind:] 
                    cap = line.split(":")
                    uri = cap[0]+":"+cap[1]+":"+cap[2]
                    file_name = arg.name
                    abs_path = os.path.abspath(pjoin('private/keys/', file_name))
                    # check if this file was created by the user
                    # TODO the public key should be in the file we get
                    if os.path.exists(abs_path):
                        with open('private/keys/'+arg.name+"public", "r") as f:
                            public = f.read() 
                    break
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
        s = str(cap[1] + salt)
        hashed_key = crypto.my_hash(s)
        ptext = crypto.decrypt(data, hashed_key[:16])   
        txt = ptext.find(SPLIT_SYMBOL)
        return ptext[:txt]

def get_data(name):
    conn = httplib.HTTPConnection(HOST_IP+":" + PORT)
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
    if arg.writecap:
        # putting with a cap requires
        # 1) Getting the encrypted private key
        # 2) Decrypting it, and using it to sign the updated data
        # 3) Signing the encryption of the updated data with the private key
        cap = arg.writecap.split(":")
        cipher = get_data(arg.writecap) 
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
            s = str(cap[1] + salt)
            hashed_key = crypto.my_hash(s)
            ptext = crypto.decrypt(data, hashed_key[:16])   
            splitted = ptext.split(SPLIT_SYMBOL)
            raw_data = splitted[0]
            enc_pk = splitted[1]
            private = crypto.decrypt(enc_pk, cap[1])
            data = arg.data
    else:
        # here cap is (my_hash(private_key), my_hash(public_key))
        (private, public, cap) = crypto.generate_RSA()
        cap = [FILE_WRITE_CAP, cap[0], cap[1]]
        # save the cap in a private file 
        with open('private/files.txt', "a") as f:
            c = arg.name+ "|" + cap[0] + ":" + cap[1] + ":" + cap[2] + "\n"
            f.write(c)
        # save the private key in a file 
        with open('private/keys/'+arg.name+"public", "w") as f:
            f.write(public)
        with open('private/keys/'+arg.name+"private", "w") as f:
            f.write(private)
        data = arg.data
    # store the encrypted private key in the data
    data = data + SPLIT_SYMBOL + crypto.encrypt(private, cap[1], False)
    # use the read key as an encryption key for the concatted data
    salt = "a"*16
    s = str(cap[1] + salt)
    hashed_key = crypto.my_hash(s)
    # encrypt the data
    data = crypto.encrypt(data, hashed_key[:16], False)
    # sign it with private key
    signature = crypto.sign_data(private, data)
    # FINAL DATA IS
    # enc_data | signature | public_key | hash(public_key)
    data = data +SPLIT_SYMBOL+ signature + SPLIT_SYMBOL + public + SPLIT_SYMBOL + crypto.my_hash(public)

    # double hash the key to get the file name
    file_name = crypto.my_hash(crypto.my_hash(cap[1]))
    write = ":".join(map(str, cap)) 
    print "Write cap for the file is: %s" % write
    cap[0] = FILE_READ_CAP
    cap[1] = crypto.my_hash(cap[1])[:16]
    read = ":".join(map(str, cap)) 
    print "Read cap for the file is: %s" % read
    print "You can access the capability in private/files.txt"
    post_data(data, write)

def ls_handler(arg):
    f = open("private/files.txt")
    for line in f:
        if arg.v:
            print line
        else:
            print line.split("|")[0]
    f.close()

def post_data(data, name):
    encoded = EncodeAES(data)
    params = urllib.urlencode({'data': encoded})
    headers = {"Content-type": "text/html/plain",
    "Accept": "text/plain"}
    conn = httplib.HTTPConnection(HOST_IP+":"+PORT)
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
                            required=False,
                            help='Get a file with name')
    get_parser.add_argument('-c',
                            '--cap',
                            required=False,
                            help='Get a file with cap')
    get_parser.add_argument('--t',
                            action='store_const',
                            const='42')
    put_parser = subparsers.add_parser('put', help='Put a file')
    put_parser.add_argument('-n',
                            '--name',
                            required=False,
                            help='Put a file with name')
    put_parser.add_argument('-d',
                            '--data',
                            required=False,
                            help='Specify file content')
                            
    put_parser.add_argument('-wc',
                            '--writecap',
                            required=False,
                            help='Put a file with cap')
    put_parser.add_argument('--t',
                            action='store_const',
                            const='42')                        
    ls_parser = subparsers.add_parser('ls', help='display names of your files')
    ls_parser.add_argument('--v',
                           action='store_const',
                           const='42')
    if shellflag:
        shell_parser = subparsers.add_parser('shell', help='start shell')

def getCapFromFilename(name):
    with open("private/files.txt") as f:
        for line in f:
            spl = line.split('|')
            fn = spl[0]
            cap = spl[1]
            if fn == name:
                return cap

def getDataFromTemp():
    data = ""
    with open("tempfile.txt") as f:
        for line in f:
            data += line
    return data

def writeToTemp(data):
    tempfile = open("tempfile.txt", "w")
    tempfile.write(data)
    tempfile.close()

def handle_args(args, parser):
    if args.mode == "get":
        try:
            data = get_handler(args)
        except TypeError as e:
            print "get failed"
        writeToTemp(data)
        if not args.t:
            launch_editor()
        filename = args.name
        cap = getCapFromFilename(filename)
        data = getDataFromTemp()
        command = "put -d '" + data + "' -wc " + cap
        args = parser.parse_args(shlex.split(command))
        if args.mode == "put":
            put_handler(args)
    elif args.mode == "put":
        writeToTemp("")
        if not args.data:
            launch_editor()
            filename = args.name
            data = getDataFromTemp()
            command = "put -n '" + filename + "' -d '" + data + "'"
            print command
            args = parser.parse_args(shlex.split(command))
            if args.mode == "put":
                put_handler(args)
        else:
            put_handler(args)
    elif args.mode == "ls":
        ls_handler(args)
    elif args.mode == "mkdir":
        print "no mkdir"
    elif args.mode == "cd":
        print "no cd"
    else:
        usage()
        
def main():

    parser = argparse.ArgumentParser(description='Run EncrypFS client')
    build_parser(parser, True)
    args = parser.parse_args()
    print '\n\n'
    handle_args(args, parser)

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

        handle_args(args, parser)

def launch_editor():
    call(["emacs", "tempfile.txt"])

if __name__ == '__main__':
    main()