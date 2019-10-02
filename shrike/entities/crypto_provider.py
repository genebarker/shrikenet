class CryptoProvider:

    def __init__(self):
        raise NotImplementedError

    def generate_hash_from_string(self, string):
        raise NotImplementedError

    def hash_matches_string(self, hash_, string):
        raise NotImplementedError
