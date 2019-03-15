import pytest
from pytest import raises
from shrike.entities.validator import Validator


class TestUsernameValidation:

    missing_message = 'username must be provided'
    out_of_range_message = (
        'username must be between {0} and {1} characters long'
        .format(Validator.username_min_length, Validator.username_max_length))
    bad_characters_message = (
        'username must be alphanumeric characters with optional underscore '
        'and period seperators')

    def test_good_username_returns_its_value(self):
        username = 'fmulder'
        assert Validator.validate_username(username) == username

    def test_username_none_throws(self):
        username = None
        expected_message = self.missing_message
        self.confirm_username_raises(expected_message, username)

    @staticmethod
    def confirm_username_raises(expected_message, given_username, field_name='username'):
        with raises(ValueError) as excinfo:
            Validator.validate_username(given_username, field_name)
        assert str(excinfo.value) == expected_message

    def test_username_none_throws_alternate_name(self):
        username = None
        alternate_field_name = 'nickname'
        expected_message = self.missing_message.replace('username', alternate_field_name)
        self.confirm_username_raises(expected_message, username, alternate_field_name)

    def test_username_empty_throws(self):
        username = ''
        expected_message = self.missing_message
        self.confirm_username_raises(expected_message, username)

    def test_username_too_short_throws(self):
        username = 'a'
        expected_message = self.out_of_range_message
        self.confirm_username_raises(expected_message, username)

    def test_username_too_short_throws_alternate_name(self):
        username = 'a'
        alternate_field_name = 'nickname'
        expected_message = self.out_of_range_message.replace('username', alternate_field_name)
        self.confirm_username_raises(expected_message, username, alternate_field_name)

    def test_username_too_large_throws(self):
        username = 'a' * (Validator.username_max_length + 1)
        expected_message = self.out_of_range_message
        self.confirm_username_raises(expected_message, username)

    def test_username_with_bad_characters_throws(self):
        username = 'no spaces'
        expected_message = self.bad_characters_message
        self.confirm_username_raises(expected_message, username)

    def test_username_with_bad_characters_throws_alternate_name(self):
        username = 'no spaces'
        alternate_field_name = 'supername'
        expected_message = self.bad_characters_message.replace('username', 'supername')
        self.confirm_username_raises(expected_message, username, alternate_field_name)

    def test_username_with_good_seperators_accepts(self):
        username = 'mr.awesome_dude'
        assert Validator.validate_username(username)

    def test_username_with_leading_seperator_throws(self):
        username = '_bad_lead_seperator'
        expected_message = self.bad_characters_message
        self.confirm_username_raises(expected_message, username)

    def test_username_with_trailing_seperator_throws(self):
        username = 'bad.trail.seperator.'
        expected_message = self.bad_characters_message
        self.confirm_username_raises(expected_message, username)


class TestNameValidation:

    missing_message = 'name must be provided'
    out_of_range_message = (
        'name must be between {0} and {1} characters long'
        .format(Validator.name_min_length, Validator.name_max_length))
    bad_characters_message = (
        'name must be alphanumeric characters with regular punctuation')

    def test_good_name_returns_its_value(self):
        name = 'Fox Mulder'
        assert Validator.validate_name(name) == name

    def test_name_none_throws(self):
        name = None
        expected_message = self.missing_message
        self.confirm_name_raises(expected_message, name)

    @staticmethod
    def confirm_name_raises(expected_message, given_name, field_name='name'):
        with raises(ValueError) as excinfo:
            Validator.validate_name(given_name, field_name)
        assert str(excinfo.value) == expected_message

    def test_name_too_short_throws(self):
        name = 'a' * (Validator.name_min_length - 1)
        expected_message = self.out_of_range_message
        self.confirm_name_raises(expected_message, name)

    @pytest.mark.parametrize(('name'), (
        ('This $has$ BAD chars'),
        ('This "has" BAD chars'),
        ('This _has_ BAD chars'),
    ))
    def test_name_with_bad_characters_throws(self, name):
        expected_message = self.bad_characters_message
        self.confirm_name_raises(expected_message, name)

    def test_name_with_permmited_punctuation_accepts(self):
        name = "Mr. BIG-Time, Jr's "
        assert Validator.validate_name(name) == name


class TestDescriptionValidation:
    
    missing_message = 'description must be provided'
    out_of_range_message = (
        'description must be between {0} and {1} characters long'
        .format(Validator.description_min_length, Validator.description_max_length))

    def test_good_description_returns_its_value(self):
        description = 'This is a good test.'
        assert Validator.validate_description(description) == description

    def test_description_none_throws(self):
        with raises(ValueError) as excinfo:
            Validator.validate_description(None)
        assert str(excinfo.value) == self.missing_message

    def test_description_too_long_throws(self):
        with raises(ValueError) as excinfo:
            Validator.validate_description('a' * (Validator.description_max_length + 1))
        assert str(excinfo.value) == self.out_of_range_message
