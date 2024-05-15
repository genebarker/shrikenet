from zxcvbn import zxcvbn

from shrikenet.entities.password_checker import PasswordChecker
from shrikenet.entities.password_strength import PasswordStrength


class zxcvbnAdapter(PasswordChecker):

    def __init__(self, min_strength=2):
        self.min_password_strength = min_strength

    def get_strength(self, password):
        results = zxcvbn(password)
        score = results["score"]
        is_too_low = True if score < self.min_password_strength else False
        suggestions = results["feedback"]["suggestions"]
        return PasswordStrength(score, is_too_low, suggestions)
