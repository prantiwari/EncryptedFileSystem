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
SPLIT_SYMBOL = "{}{}"
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

# unpackage decoded data received from server and validate, decrypt
def unpackage_data(cap, cipher):
    try:
        data_ar = cipher.split(SPLIT_SYMBOL)
        sign = data_ar[1]
        data = data_ar[0]
        public = data_ar[2]
        assert(data_ar[3] == my_hash(public))

        valid = verify_RSA(public, sign, data)
        assert(valid)
    except AssertionError  as e:
        print "Validation failed"
    
    # generate the AES decryption key and decrypt
    salt = "a"*16
    s = str(cap[1] + salt)
    hashed_key = my_hash(s)
    ptext = decrypt(data, hashed_key[:16])   
    splitted = ptext.split(SPLIT_SYMBOL)
    raw_data = splitted[0]
    enc_pk = splitted[1]
    private = decrypt(enc_pk, cap[1])
    return (raw_data, private, public)
# package the data for sending over HTTP
def package_data(data, cap, private, public):
    # store the encrypted private key in the data
    data = data + SPLIT_SYMBOL + encrypt(private, cap[1], False)
    # use the read key as an encryption key for the concatted data
    salt = "a"*16
    s = str(cap[1] + salt)
    hashed_key = my_hash(s)
    # encrypt the data
    data = encrypt(data, hashed_key[:16], False)
    # sign it with private key
    signature = sign_data(private, data)
    # FINAL DATA IS
    # enc_data | signature | public_key | hash(public_key)
    data = data +SPLIT_SYMBOL+ signature + SPLIT_SYMBOL + public + SPLIT_SYMBOL + my_hash(public)
    return data
