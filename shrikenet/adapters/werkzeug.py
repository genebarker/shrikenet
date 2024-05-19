from werkzeug.security import check_password_hash, generate_password_hash

from shrikenet.entities.crypto_provider import CryptoProvider


class WerkzeugAdapter(CryptoProvider):

    def __init__(self):
        pass

    def generate_hash_from_string(self, string):
        return generate_password_hash(string)

    def hash_matches_string(self, hash_, string):
        if hash_ is None or string is None:
            return False
        return check_password_hash(hash_, string)
