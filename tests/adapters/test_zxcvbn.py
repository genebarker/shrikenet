from shrikenet.adapters.zxcvbn import zxcvbnAdapter
from shrikenet.entities.password_checker import PasswordChecker
from shrikenet.entities.password_strength import PasswordStrength


def test_is_a_password_checker():
    checker = zxcvbnAdapter()
    assert isinstance(checker, PasswordChecker)


def test_default_minimum_strength_is_two():
    checker = zxcvbnAdapter()
    assert checker.min_password_strength == 2


def test_minimum_strength_can_be_set_on_init():
    min_strength = 3
    checker = zxcvbnAdapter(min_strength)
    assert checker.min_password_strength == 3


def test_get_strength_returns_strength_object():
    checker = zxcvbnAdapter()
    strength = checker.get_strength("somePassword")
    assert isinstance(strength, PasswordStrength)


def test_get_strength_returns_too_low_for_horrible_password():
    checker = zxcvbnAdapter()
    strength = checker.get_strength("password")
    assert strength.is_too_low


def test_get_strength_returns_score_of_zero_for_horrible_password():
    checker = zxcvbnAdapter()
    strength = checker.get_strength("password")
    assert strength.score == 0


def test_get_strength_returns_not_too_low_for_strong_password():
    checker = zxcvbnAdapter()
    strength = checker.get_strength("thisIsPrettyStrong")
    assert strength.is_too_low is False


def test_get_strength_returns_high_score_for_strong_password():
    checker = zxcvbnAdapter()
    strength = checker.get_strength("thisIsPrettyStrong")
    assert strength.score == 4


def test_get_strength_returns_suggestions_for_horrible_password():
    checker = zxcvbnAdapter()
    strength = checker.get_strength("password")
    assert "Add another word or two." in strength.suggestions[0]
