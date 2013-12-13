#!/usr/bin/python

from subprocess import call
import sys
import os

#Testing if making a file works
def test1():
    put = os.system("python client.py put -n 'test1.txt' -d 'asdfasf' > 1.out")
    assert(put == 0)

    f = open("o.out", "r")
    output = f.read()

    f.close()
    

#Testing to see if can get file
def test2():
    put = os.system("python client.py put -n 'test2.txt' -d 'asdfasdf' > 2.out")
    assert(put == 0)
    
    get = os.system("python client.py get -n 'test2.txt' --t > g2.out")
    assert(get == 0)
    
    f = open("g2.out", "r")
    expected = "asdfasdf"  
    
    output = f.read()
    sp = output.split("\n")[5].split(":")[1].strip()
    
    print output
    print "sp", sp

    assert(sp[len(sp)-1] == expected)
    
    f.close()

#Testing to see if still returned after malicious behavior
def test3():
    x = os.system("python client.py put -n 'test3.txt' -d 'asdfasf' > o.out")
    f = open("o.out", "r")
    output = f.read()
    
    f.close()

    
if len(sys.argv) != 1:
    if sys.argv[1] == '1':
        test1()
    if sys.argv[1] == "2":
        test2()
else:
    test1()
    test2()
    test3()
