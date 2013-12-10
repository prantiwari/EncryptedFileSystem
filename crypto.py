from Crypto.Cipher import AES
from Crypto.Hash import SHA
import os

PADDING = '{'
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
# return (cap, encrypted_data) given the data
# cap = (key, SHA(cipher))
def encrypt(data):
    # random key
    key = os.urandom(16) 
    obj = AES.new(key, AES.MODE_ECB)
    cipher = obj.encrypt(pad(data))
    cap = (key, hash(cipher))
    return (cap, cipher)

# return decrypted version of the data 
def decrypt(data, key):
    obj = AES.new(key, AES.MODE_ECB)
    plain = obj.decrypt(data)
    return plain.rstrip(PADDING)

# verify integrity of the data
def verify(cipher, cap):
    (key, h) = cap
    print "CAP is : ", cap
    print "Stored hash is: ", h
    print "Calculated hash is: ", hash(cipher)
    return hash(cipher) == h    
    
# just SHA hash of the data
def hash(data):
    h = SHA.new()
    h.update(data)
    return h.hexdigest()    
