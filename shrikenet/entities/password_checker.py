from shrikenet.entities.PasswordStrength import PasswordStrength


class PasswordChecker:

    def __init__(self):
        self.is_too_low = False

    def get_strength(self, password):
        is_too_low = True if (password == "password") else False
        suggestions = [
            "no suggestion",
        ]
        return PasswordStrength(is_too_low, suggestions)
