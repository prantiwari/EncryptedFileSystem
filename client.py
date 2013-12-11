#!/usr/bin/env python
# Initial client version.
import httplib, urllib, getopt
import argparse
import crypto
import base64
import sys
import shlex

# Helpers to encode and decode a string with base64
EncodeAES = lambda s: base64.b64encode(s) 
DecodeAES = lambda e: base64.b64decode(e)
def get_handler(arg):
    with open('private/files.txt', "r") as f:
        for line in f:
            ind = line.find(arg.name)
            # here assumes the files have different names
            # TODO check for the same names that are substring of the other
            if ind != -1:
                key_ind = line.find("|")+1
                hash_ind = line.rfind(":")
                end_ind = line.find("\n") 
                cap = (line[key_ind:hash_ind], line[hash_ind+1:end_ind])
                print "CAP for the file is: ", cap
                break
    hash = crypto.hash(crypto.hash(cap[0]))
    print "HASH of the key: ", hash
    cipher = get_data(hash)
    print "RECEIVED CIPHER: ", cipher
    valid = crypto.verify(cipher, cap)
    print "VAlid: ", valid
    if valid:
        ptext = crypto.decrypt(cipher, cap[0])   
        print "Decrypted file is: ", ptext

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
    print "Data in the file is: "+ data
    conn.close()
    return data
    
def put_handler(arg):
    (cap, data) = crypto.encrypt(arg.data)
    # save the cap in a private file 
    with open('private/files.txt', "a") as f:
        c = arg.name+ "|" + cap[0] + ":" + cap[1] + "\n"
        print "CAPABILITY: " ,c
        f.write(c)

    # double hash the key to get the file name
    file_name = crypto.hash(crypto.hash(cap[0]))
    print "Storage index: ",file_name
    post_data(data, file_name)  

def post_data(data, name):
    print "STORED CIPHER IS: ", data
    encoded = EncodeAES(data)
    print "Encoded data: ", 
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
