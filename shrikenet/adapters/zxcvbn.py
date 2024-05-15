from zxcvbn import zxcvbn

from shrikenet.entities.password_checker import PasswordChecker
from shrikenet.entities.password_strength import PasswordStrength


class zxcvbnAdapter(PasswordChecker):

    def __init__(self, min_strength=2):
        self.min_password_strength = min_strength

    def get_strength(self, password):
        results = zxcvbn(password)

        score = results["score"]
        is_too_low = score < self.min_password_strength
        suggestion_list = results["feedback"]["suggestions"]
        if len(suggestion_list) > 0:
            suggestion = suggestion_list[0]
        else:
            suggestion = "None."

        return PasswordStrength(score, is_too_low, suggestion)
