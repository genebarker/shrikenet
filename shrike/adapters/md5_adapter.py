import hashlib

from shrike.entities.crypto_provider import CryptoProvider

class MD5Adapter(CryptoProvider):

    def __init__(self):
        pass

    def generate_hash_from_string(self, password):
        return hashlib.md5(password.encode('utf8')).hexdigest()

    def hash_matches_string(self, hash_, string):
        if string is None:
            return False
        return hash_ == self.generate_hash_from_string(string)
