import pytest

from shrikenet.entities.password_checker import PasswordChecker


def test_interface_cant_be_instantiated():
    with pytest.raises(NotImplementedError):
        PasswordChecker()


@pytest.fixture
def password_checker():
    class FakeChecker(PasswordChecker):
        def __init__(self):
            pass

    return FakeChecker()


def test_get_strength_method_cant_be_called(password_checker):
    with pytest.raises(NotImplementedError):
        password_checker.get_strength("somePassword")
