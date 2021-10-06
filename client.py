#!/usr/bin/env python
# Initial client version.
import http.client, urllib, getopt
import argparse
import crypto
import base64
import sys
import shlex
import os
import subprocess
import json
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
DIR_WRITE_CAP = "DIR-WR"

# TODO Convert all file read to json
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
                    uri = capToString(cap)
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
<<<<<<< HEAD

    assert(data_ar[3] == crypto.my_hash(public))

    valid = crypto.verify_RSA(public, sign, data)
    print ("Valid: ", valid)
    if valid:
        # generate the AES decryption key and decrypt
        salt = "a"*16
        s = str(cap[1] + salt)
        hashed_key = crypto.my_hash(s)
        ptext = crypto.decrypt(data, hashed_key[:16])
        txt = ptext.find(SPLIT_SYMBOL)
        return ptext[:txt]
    return None
=======
    try:
        assert(data_ar[3] == crypto.my_hash(public))
        valid = crypto.verify_RSA(public, sign, data)
        print "Valid: ", valid
        assert(valid)
    except AssertionError  as e:
        print "Data invalid"
        return
    # generate the AES decryption key and decrypt
    salt = "a"*16
    s = str(cap[1] + salt)
    hashed_key = crypto.my_hash(s)
    ptext = crypto.decrypt(data, hashed_key[:16])   
    txt = ptext.find(SPLIT_SYMBOL)
    return ptext[:txt]
>>>>>>> working

def get_data(name):
    conn = httplib.HTTPConnection(HOST_IP+":" + PORT)
    conn.request("GET", "/"+name)
    r1 = conn.getresponse()
<<<<<<< HEAD
    print (r1.status, r1.reason)
=======
>>>>>>> working
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

<<<<<<< HEAD
=======
def mkdir_handler(arg):
    if arg.path:
        # TODO do recursive get on the path /a/b/c/
        # TODO assert somehow that the path exists on the server
        return
    else:
        if arg.root:
            # create root dir
            (root_private, root_public, cap) = crypto.generate_RSA()
            root_cap = [DIR_WRITE_CAP, cap[0], cap[1]]
            data = {".": ":".join(root_cap)}
            print "ROOT CAP: ", root_cap
            with open("private/root_dir.cap", 'w') as f:
                c = arg.name + "|" + capToString(root_cap) + "\n"
                f.write(c)
        else:
            # assume the root exists 
            with open("private/root_dir.cap", 'r') as f:
                line = f.read()
                if line and line != "\n":
                    line = line[line.find("|")+1:].strip("\n")
                    root_cap = line.split(":")
                    root_cap[2] = root_cap[2]
                    cipher = get_data(line)
                    (data, root_private, root_public)= crypto.unpackage_data(root_cap, cipher) 
                    data = json.loads(data) 
                    (private, public, cap) = crypto.generate_RSA()
                    cap = [DIR_WRITE_CAP, cap[0], cap[1]]
                    data[arg.name] =  ":".join(cap)
                    print "APPENDED DATA: ", data
                    # post new dir 1st 
                    new_data = {".": ":".join(cap)}
                    new_data = json.dumps(new_data)
                    new_data = crypto.package_data(new_data, cap, private, public)
                    print_capabilities(cap)
                    post_data(new_data, capToString(cap))
                    print "NEW DIR POSTED"
                else:
                    return
    # post root dir data 
    data = json.dumps(data) 
    data = crypto.package_data(data, root_cap, root_private, root_public)
    print_capabilities(root_cap)
    post_data(data, capToString(root_cap))
    print "ROOT UPDATED"

def rn_handler(arg):
    #assume root exists
    with open("private/root_dir.cap", 'r') as f:
        line = f.read()
        if line and line != "\n":
            line = line[line.find("|")+1:].strip("\n")
            root_cap = line.split(":")
            root_cap[2] = root_cap[2]
            cipher = get_data(line)
            (data, root_private, root_public)= crypto.unpackage_data(root_cap, cipher) 
            data = json.loads(data) 
            print "DATA BEFORE: " + str(data)
            data[arg.newfilename] = data[arg.filename]
            del data[arg.filename]
            print "DATA AFTER: " + str(data)
            #print "APPENDED DATA: ", data
            # post new dir 1st 
            data = json.dumps(data)
            new_data = crypto.package_data(data, root_cap, root_private, root_public)
            print_capabilities(root_cap)
            post_data(new_data, capToString(root_cap))
            print "ROOT UPDATED"
            return
        else:
            print "rn failed"
            return
"""
def update_root(uri, new_data):
    cipher = get_data(uri)
    (data, root_private, root_public)= crypto.unpackage_data(root_cap, cipher) 
    data = json.loads(data) 
    data[new_data[0]] =  ":".join(new_data[1])
    data = json.dumps(data) 
    data = crypto.package_data(data, root_cap, root_private, root_public)
    print_capabilities(root_cap)
    post_data(data, capToString(root_cap))
"""
>>>>>>> working
def put_handler(arg):
    if arg.writecap:
        # putting with a cap requires
        # 1) Getting the encrypted private key
        # 2) Decrypting it, and using it to sign the updated data
        # 3) Signing the encryption of the updated data with the private key
        cap = arg.writecap.split(":")
<<<<<<< HEAD
        cipher = get_data(arg.writecap)
        data_ar = cipher.split(SPLIT_SYMBOL)
        sign = data_ar[1]
        data = data_ar[0]
        public = data_ar[2]
        assert(data_ar[3] == crypto.my_hash(public))

        valid = crypto.verify_RSA(public, sign, data)
        print ("Valid: ", valid)
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
=======
        cipher = get_data(arg.writecap) 
        
        (data, private, public) = crypto.unpackage_data(cap, cipher)
    
>>>>>>> working
    else:
        with open("private/root_dir.cap", 'r') as f:
            line = f.read()
            if line and line != "\n":
                line = line[line.find("|")+1:].strip("\n")
                root_cap = line.split(":")
                cipher = get_data(line)
                (data, root_private, root_public)= crypto.unpackage_data(root_cap, cipher) 
                data = json.loads(data)
 
        # here cap is (my_hash(private_key), my_hash(public_key))
        (private, public, cap) = crypto.generate_RSA()
        cap = [FILE_WRITE_CAP, cap[0], cap[1]]
<<<<<<< HEAD
        # save the cap in a private file
=======
        # put name in dir
        data[arg.name] = capToString(cap)         
        # update root dir data 
        data = json.dumps(data) 
        data = crypto.package_data(data, root_cap, root_private, root_public)
        print_capabilities(root_cap)
        post_data(data, capToString(root_cap))
        # save the cap in a private file 
>>>>>>> working
        with open('private/files.txt', "a") as f:
            c = arg.name+ "|" + capToString(cap)+ "\n"
            f.write(c)
<<<<<<< HEAD
        # save the private key in a file
=======
        # TODO get rid of key storage by making get to the server via URI after createion
        # save the private key in a file 
>>>>>>> working
        with open('private/keys/'+arg.name+"public", "w") as f:
            f.write(public)
        with open('private/keys/'+arg.name+"private", "w") as f:
            f.write(private)
    data = arg.data
    data = crypto.package_data(data, cap, private, public)
    print_capabilities(cap)
    post_data(data, capToString(cap))

def print_capabilities(cap):
    if cap[0] == FILE_WRITE_CAP:
        t = "file"
        r = FILE_READ_CAP
    elif cap[0] == DIR_WRITE_CAP:
        t = "directory"
        r = DIR_READ_CAP
    else:
        t = "unknown"
        r = "unknown"
    # double hash the key to get the file name
<<<<<<< HEAD
    file_name = crypto.my_hash(crypto.my_hash(cap[1]))
    write = ":".join(map(str, cap))
    print ("Write cap for the file is: %s" % write)
    cap[0] = FILE_READ_CAP
    cap[1] = crypto.my_hash(cap[1])[:16]
    read = ":".join(map(str, cap))
    print ("Read cap for the file is: %s" % read)
    print ("You can access the capability in private/files.txt")
    post_data(data, write)

def ls_handler(arg):
    f = open("private/files.txt")
    for line in f:
        if arg.v:
            print (line)
        else:
            print (line.split("|")[0])
    f.close()
=======
    h = crypto.my_hash(cap[1])[:16]
    file_name = crypto.my_hash(h)
    write = capToString(cap) 
    print "Write cap for the %s is: %s" % (t, write)
    read = capToString(cap)
    print "Read cap for the %s is: %s" % (t, capToString((r, h, cap[2])))

def ls_handler(arg):
    # ls path by getting the file content
    if arg.path:
        return      
    else:
        # ls root 
        with open("private/root_dir.cap", 'r') as f:
            line = f.read()
            if line and line != "\n":
                line = line[line.find("|")+1:].strip("\n")
                cap = line.split(":")
                print "CAP: ", cap
                cipher = get_data(line)
                (data, private, public)= crypto.unpackage_data(cap, cipher) 
            else:
                return
    # TODO pretty print data
    data = json.loads(data) 
    print data.keys()
>>>>>>> working

def rm_handler(arg):
    print( arg.file)

<<<<<<< HEAD
def rn_handler(arg):
    print ("The old file name is " + arg.filename)
    print ("The new file name is " + arg.newfilename)

=======
>>>>>>> working
def post_data(data, name):
    encoded = EncodeAES(data)
    params = urllib.urlencode({'data': encoded})
    headers = {"Content-type": "text/html/plain",
    "Accept": "text/plain"}
    conn = httplib.HTTPConnection(HOST_IP+":"+PORT)
    conn.request("POST", "/"+ name, params, headers)
    
    response = conn.getresponse()
<<<<<<< HEAD
    print (response.status, response.reason)
=======

>>>>>>> working
    data = response.read()
    conn.close()
def usage():
    print (' -------------------------------------------------------------------------')

    print (' This is EncrypFS file system')
    print (' ')
    print (' Usage:')
    print (' client.py --h')
    print (' client.py --g my_name.txt')
    print (' client.py --p my_name.txt "THIS IS A TEST DATA"')
    print (' ')
    print (' --g Get the file with the name')
    print (' --p  Put the file and data')
    print (' -------------------------------------------------------------------------')
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

    put_parser.add_argument('-c',
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
    ls_parser.add_argument('-p',
                              '--path',
                              required=False,
                              help='Directory to list')
    mkdir_parser = subparsers.add_parser('mkdir', help='Make a directory')
    mkdir_parser.add_argument('-p',
                              '--path',
                              required=False,
                              help='Directory in which to create the directory')
    mkdir_parser.add_argument('-n',
                            '--name',
                            required=True,
                            help='Dir name')
    mkdir_parser.add_argument('-r',
                              '--root',
                              required=False,
                              action='store_true',
                              default=False,
                              help='Create root directory')
    rm_parser = subparsers.add_parser('rm', help='remove a file')
    rm_parser.add_argument('file')

    rn_parser = subparsers.add_parser('rn', help='rename a file')
    rn_parser.add_argument('filename')
    rn_parser.add_argument('newfilename')

    if shellflag:
        shell_parser = subparsers.add_parser('shell', help='start shell')
# helpers
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

def capToString(cap):
    return ":".join(cap)


def handle_args(args, parser):
    if args.mode == "get":
        try:
            data = get_handler(args)
        except TypeError as e:
            print ("get failed")
            return None
        if not data:
            print ("INVALID/CORRUPTED DATA")
            return None
        writeToTemp(data)
        if not args.t:
            launch_editor()
<<<<<<< HEAD
            filename = args.name
            cap = getCapFromFilename(filename)
            newdata = getDataFromTemp()
            command = "put -d '" + newdata + "' -c " + cap
            args = parser.parse_args(shlex.split(command))
            if args.mode == "put":
                put_handler(args)
        else:
            print (data)
=======
        filename = args.name
        cap = getCapFromFilename(filename)
        data = getDataFromTemp()
        command = "put -d '" + data + "' -c " + cap
        args = parser.parse_args(shlex.split(command))
        if args.mode == "put":
            put_handler(args)
>>>>>>> working
    elif args.mode == "put":
        writeToTemp("")
        if not args.data:
            launch_editor()
            filename = args.name
            data = getDataFromTemp()
            command = "put -n '" + filename + "' -d '" + data + "'"
            print (command)
            args = parser.parse_args(shlex.split(command))
            if args.mode == "put":
                put_handler(args)
        else:
            put_handler(args)
    elif args.mode == "shell":
        shell()
    elif args.mode == "ls":
        ls_handler(args)
    elif args.mode == "mkdir":
<<<<<<< HEAD
        print ("no mkdir")
=======
        mkdir_handler(args)
>>>>>>> working
    elif args.mode == "cd":
        print ("no cd")
    elif args.mode == "rm":
        rm_handler(args)
    elif args.mode == "rn":
        rn_handler(args)

    else:
        usage()

def main():

    parser = argparse.ArgumentParser(description='Run EncrypFS client')
    build_parser(parser, True)
    args = parser.parse_args()
    print ('\n\n')
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
