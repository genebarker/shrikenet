from dataclasses import dataclass


@dataclass
class PasswordStrength:
    score: int = 0
    is_too_low: bool = False
    suggestion: str = "None."
