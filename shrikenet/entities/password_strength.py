from dataclasses import dataclass
from typing import List


@dataclass
class PasswordStrength:
    score: int = 0
    is_too_low: bool = False
    suggestions: List[str] = None
