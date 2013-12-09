#!/usr/bin/env python
# Initial client version.
import httplib, urllib, getopt
import argparse

def get_handler(arg):
    conn = httplib.HTTPConnection("localhost:8000")
    conn.request("GET", "/"+arg.name)
    r1 = conn.getresponse()
    print r1.status, r1.reason
    data1 = r1.read()
    print "Data in the file is: "+ data1
    conn.close()
    
def put_handler(arg):
    params = urllib.urlencode({'data': arg.data})
    headers = {"Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"}
    conn = httplib.HTTPConnection("localhost:8000")
    conn.request("POST", "/"+ arg.name, params, headers)
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

    
def main():

    parser = argparse.ArgumentParser(description='Run EncrypFS client')
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
    args = parser.parse_args()
    print '\n\n'
    if args.mode == "get":
        get_handler(args)
    elif args.mode == "put":
        put_handler(args)
    else:
        usage()

if __name__ == '__main__':
    main()