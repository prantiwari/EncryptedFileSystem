from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import Crypto.Random
from base64 import b64decode, b64encode
import os

SALT_SIZE= 16 
PADDING = '{'
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
# return (cap, encrypted_data) given the data
# cap = (key, SHA(cipher))
def encrypt(data, key=None, cap=True):
    if key == None:
        # random key
        key = os.urandom(16) 
    obj = AES.new(key, AES.MODE_ECB)
    cipher = obj.encrypt(pad(data))
    if cap:
        cap = (key, my_hash(cipher))
        return (cap, cipher)
    else:
        return cipher
# here cap is (hash(private_key), hash(public_key))
# return: (cap, cipher)
def encrypt_RSA(data, public):
    rsakey = RSA.importKey(public)
    rsakey = PKCS1_OAEP.new(rsakey)    
    encrypted = rsakey.encrypt(data)
    encrypted = encrypted.encode('base64')
    return  encrypted
def generate_RSA (bits=2048):
    """
    Generare an RSA pair with an exponent of 65537 in PEM format
    param: bits in the key length in bits
    Return private key and public key    
    """
    new_key = RSA.generate(bits, e=65537)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")
    cap = (my_hash(private_key)[:16], my_hash(public_key)[:16])
    return (private_key, public_key, cap)
# return decrypted version of the data 
def decrypt(data, key):
    obj = AES.new(key, AES.MODE_ECB)
    plain = obj.decrypt(data)
    return plain.rstrip(PADDING)

# return RSA decrypted data with the private key
def decrypt_RSA(data, private_key):
    rsakey = RSA.importKey(private_key)
    rsakey = PKCS1_OAEP.new(rsakey)
    dec = rsakey.decrypt(b64decode(data)) 
    return dec
# verify integrity of the data
def verify(cipher, cap):
    (key, h) = cap
    return my_hash(cipher) == h    

# verify via RSA 
def verify_RSA(public_key, signature, data):
    rsakey = RSA.importKey(public_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(data)
    if signer.verify(digest,signature):
        return True
    return False
# sign data via RSA public key
def sign_data(private_key, data):
    rsakey = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(data)    
    sign = signer.sign(digest)
    return sign

# just SHA hash of the data
def my_hash(data):
    h = SHA.new()
    h.update(data)
    return h.hexdigest()    
