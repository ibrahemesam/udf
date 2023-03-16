class xor:
    KEY = [174,191,86,120,171,205,239,241]
    SEND_KEY = []
    RECEIVE_KEY = []

    def __init__(self):
        self.SEND_KEY = self.KEY.copy()
        self.RECEIVE_KEY = self.KEY.copy()

    def encrypt(self, arr, key=None):
        if key is None:
            key = self.SEND_KEY
        arr[0] = (arr[0] ^ key[0]) % 256;
        idx = 1
        while idx < len(arr):
            key[idx % 8] = (key[idx % 8] + arr[idx - 1] ^ idx) % 256;
            arr[idx] = ((arr[idx] ^ key[idx % 8]) + arr[idx - 1]) % 256;
            idx += 1
        return arr

    def decrypt(self, enc, key=None):
        if key is None:
            key = self.RECEIVE_KEY
        dec = enc.copy()
        idx = 1
        dec[0] = (enc[0] ^ key[0]) % 256;
        while idx < len(enc):
            key[idx % 8] = (key[idx % 8] + enc[idx - 1] ^ idx) % 256;
            dec[idx] = (enc[idx] - enc[idx - 1] ^ key[idx % 8]) % 256;
            idx+=1
        return dec
    def encrypt_once(self, byts):
        return bytes(self.encrypt(bytearray(byts), self.KEY.copy()))
    def decrypt_once(self, byts):
        return bytes(self.decrypt(bytearray(byts), self.KEY.copy()))
