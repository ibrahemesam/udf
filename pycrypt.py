from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

class RSA_crypt:
    def __init__(self):
        pem_key = b'''MIICWwIBAAKBgH3iz2reb245Wmws43AnuRYqTzTh7Zn3VxhrLfJa9lTcVDmxeAt6
        8LpA8aVyqzxV0PSWsFXOzTssLMpMILODONq7ZgEPPsSXq76vrXCnRVQcZgyVvuCo
        wtsicb6SQuKjSr7fr5zwZcIvyS4b1hoFmJHcuMTdbOKrk24p521nWlTbAgMBAAEC
        gYBCiTHWK3E8EgZP7L3dlrFGHOC2c7+QxGF9X5DuatON8NJ3l+x6LOW1nAPczanh
        /v2teUQEZoSlBOk7l1clanMOs1s6otOwF4G1kxD08mgNGdM/7sB6ohr6w83rcPRl
        EBn66KhFgbiLfly/7/PAQusUK6CjFI44aePKbFTVz4/BYQJBALqPTXBSU6CggVLo
        svUFBWl46EbicB0/79APxAgN0VYokGdLG5uC0Eq1gc+enQV9GxI/2x6AqidvABB4
        aSEeYSsCQQCsvhdewbtqZYG/mvZbTyiaDBo8GdZQvrHVJToR1PJJe3dbs4ffS7Bm
        meeb2hITsIt4w6QFsxARLIj/+pP+pyMRAkEAsdFZHFA8CYQy/9VwjX4ltGxb6QR3
        nEmOyJ/eV1bkSt0LFolOXSGIa00p17z1KYAfR3u53Q8CH+f7BbffbIPKVQJAVYd1
        SMyBgCesO3N9oS4re0Kcxr9ANxCEOnXJL8URBcMlEPluP+hY+iQf4jHyG1+hXvT3
        RH8paGd1mdC28DJPEQJATKGQUFVHTFiMTxoLki4XKtHGrBmiKqqERfFIpE7/xxTq
        YMpICI6zcKKKAFgpuZ5c9K35+8i4YlgJFwBNwRyC0g=='''
        key = base64.b64decode(pem_key)
        keyPriv = RSA.importKey(key)
        private_key = RSA.construct((keyPriv.n, keyPriv.e, keyPriv.d, keyPriv.p, keyPriv.q))
        # publickey = keyPriv.public_key()
        self.chiper = PKCS1_v1_5.new(private_key)

    def encrypt(self, string): #encryptToBase64Str
        p = bytearray(string.encode())
        c = self.chiper.encrypt(p)
        return base64.b64encode(c).decode()
        
    def encryptBytes(self, byts):
        return self.chiper.encrypt(byts)

    def decrypt(self, str_bs64): #decryptFromBase64Str
        c = base64.b64decode(str_bs64)
        c = bytearray(c)
        p = self.chiper.decrypt(c, None)
        try:
            if p.startswith(b'\x00'): p = p[2:]
            return p.decode()
        except: pass


    def decryptBytes(self, byts):
        '''while True:
            if len(byts) != 128:
                byts = b'\x00' + byts
            else: break'''
        c = bytearray(byts)
        #print(c)
        #print(len(c))
        p = self.chiper.decrypt(c, )
        print(p)
        if p.startswith(b'\x00'): p = p[2:]
        return p.decode()

class HEX_crypt:
    def __init__(self): pass

    @staticmethod
    def encryptBytes(byts, number_of_encryptions=1):
        for i in range(number_of_encryptions):
            byts = byts.hex().encode()
        return byts.decode()

    @staticmethod
    def encrypt(string, number_of_encryptions=1):
        return HEX_crypt.encryptBytes(string.encode(), number_of_encryptions)

    @staticmethod
    def decrypt(string, number_of_decryptions=1):
        for i in range(number_of_decryptions):
            string = bytes.fromhex(string).decode()
        return string
        
    @staticmethod
    def decryptBytes(string, number_of_decryptions=1):
        for i in range(number_of_decryptions):
            string = bytes.fromhex(string)
            try: string = string.decode()
            except: break
        return string
