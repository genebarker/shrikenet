from shrike.entities.crypto_provider import CryptoProvider


class SwapcaseAdapter(CryptoProvider):

    def __init__(self):
        pass

    def generate_hash_from_string(self, password):
        return password.swapcase() 

    def hash_matches_string(self, hash_, string):
        if string is None:
            return False
        return hash_ == self.generate_hash_from_string(string)
