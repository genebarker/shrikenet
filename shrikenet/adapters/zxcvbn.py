from zxcvbn import zxcvbn

from shrikenet.entities.password_checker import PasswordChecker
from shrikenet.entities.password_strength import PasswordStrength


class zxcvbnAdapter(PasswordChecker):

    def __init__(self):
        pass

    def get_strength(self, password):
        results = zxcvbn(password)
        is_too_low = True if (results["score"] < 2) else False
        suggestions = None
        return PasswordStrength(is_too_low, suggestions)
