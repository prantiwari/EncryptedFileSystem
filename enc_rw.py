from Crypto.Cipher import AES

def read_enc(key, ciphname):

    obj = AES.new(key, AES.MODE_CBC)

    f = open(ciphname, "r")
    c = f.read()
    
    return obj.decrypt(c)


def write_enc(key, ciphname, text):

    obj = AES.new(key, AES.MODE_CBC)

    f = open(ciphname, "w")

    newf =  open("temp"+ciphname, "w")

    plain = obj.decrypt(f.read())

    newf.write(plain)
    newf.write(text)

    c = obj.encrypt(newf.read)
