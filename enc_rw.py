#!/usr/bin/python              

from Crypto.Cipher import AES
import os

def read_enc(key, ciphname):

    obj = AES.new(key, AES.MODE_ECB)

    f = open(ciphname, "r")
    c = f.read()
    
    return obj.decrypt(c)


def write_enc(key, ciphname, text):

    obj = AES.new(key, AES.MODE_ECB)

    f = open(ciphname, "r+")

    # create new temp file
    newf =  open("temp"+ciphname, "w")
    newf.close()
    newf =  open("temp"+ciphname, "r+")
    
    # copy file content to temp file 
    cipher = f.read()
    f.close()
    plain = str(obj.decrypt(cipher))
    newf.write(plain)

    # add new content to temp file
    newf.write(text)
    newf.close()

    # encrypt old and new content
    newf =  open("temp"+ciphname, "r+")    
    ciph = newf.read()
    c = obj.encrypt(ciph)

    # write new encrypted content to file
    with open(ciphname, "w") as f:
        f.write(c)
    f.close()
    newf.close()
    
    #delete temp file
    os.remove("temp"+ciphname)
    

obj = AES.new("asdfasdfasdfasdf", AES.MODE_ECB) 
fileA = open("test", "w")

secret = "Secret text that should be encry"
cipher = obj.encrypt(secret)

fileA.write(cipher)
fileA.close()

print read_enc("asdfasdfasdfasdf", "test")

write_enc("asdfasdfasdfasdf", "test", "the cat jumped over the hot roof")

print read_enc("asdfasdfasdfasdf", "test")

# if you cat the file, you will see that it is still encrypted
