import pytest

from shrike.entities.field_validator import FieldValidator


class TestOIDValidation:

    missing_message = 'oid must be provided'
    bad_value_message = 'oid must be a positive integer'

    def test_good_returns_its_value(self):
        oid = 100
        assert FieldValidator.validate_oid(oid) == oid

    def test_none_raises(self):
        oid = None
        expected_message = self.missing_message
        self.confirm_raises(expected_message, oid)

    @staticmethod
    def confirm_raises(expected_message, given_oid, field_name='oid'):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_oid(given_oid, field_name)
        assert str(excinfo.value) == expected_message

    def test_none_with_alternate_name_raises(self):
        oid = None
        alternate_field_name = 'seqnum'
        expected_message = self.missing_message.replace('oid', alternate_field_name, 1)
        self.confirm_raises(expected_message, oid, alternate_field_name)

    @pytest.mark.parametrize(('oid'), (
        ('not a number'),
        (100.1),
    ))
    def test_non_integer_raises(self, oid):
        expected_message = self.bad_value_message
        self.confirm_raises(expected_message, oid)

    def test_negative_integer_raises(self):
        expected_message = self.bad_value_message
        self.confirm_raises(expected_message, -100)


class TestUsernameValidation:

    missing_message = 'username must be provided'
    out_of_range_message = (
        'username must be between {0} and {1} characters long'
        .format(FieldValidator.username_min_length, FieldValidator.username_max_length))
    bad_characters_message = (
        'username must be alphanumeric characters with optional underscore '
        'and period seperators')

    def test_good_returns_its_value(self):
        username = 'fmulder'
        assert FieldValidator.validate_username(username) == username

    def test_none_raises(self):
        username = None
        expected_message = self.missing_message
        self.confirm_raises(expected_message, username)

    @staticmethod
    def confirm_raises(expected_message, given_username, field_name='username'):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_username(given_username, field_name)
        assert str(excinfo.value) == expected_message

    def test_none_with_alternate_name_raises(self):
        username = None
        alternate_field_name = 'nickname'
        expected_message = self.missing_message.replace('username', alternate_field_name)
        self.confirm_raises(expected_message, username, alternate_field_name)

    def test_empty_raises(self):
        username = ''
        expected_message = self.missing_message
        self.confirm_raises(expected_message, username)

    def test_too_short_raises(self):
        username = 'a'
        expected_message = self.out_of_range_message
        self.confirm_raises(expected_message, username)

    def test_too_short_with_alternate_name_raises(self):
        username = 'a'
        alternate_field_name = 'nickname'
        expected_message = self.out_of_range_message.replace('username', alternate_field_name)
        self.confirm_raises(expected_message, username, alternate_field_name)

    def test_too_large_raises(self):
        username = 'a' * (FieldValidator.username_max_length + 1)
        expected_message = self.out_of_range_message
        self.confirm_raises(expected_message, username)

    def test_bad_characters_raises(self):
        username = 'no spaces'
        expected_message = self.bad_characters_message
        self.confirm_raises(expected_message, username)

    def test_bad_characters_with_alternate_name_raises(self):
        username = 'no spaces'
        alternate_field_name = 'supername'
        expected_message = self.bad_characters_message.replace('username', 'supername')
        self.confirm_raises(expected_message, username, alternate_field_name)

    def test_good_seperators_validate(self):
        username = 'mr.awesome_dude'
        assert FieldValidator.validate_username(username) == username

    def test_leading_seperator_raises(self):
        username = '_bad_lead_seperator'
        expected_message = self.bad_characters_message
        self.confirm_raises(expected_message, username)

    def test_trailing_seperator_raises(self):
        username = 'bad.trail.seperator.'
        expected_message = self.bad_characters_message
        self.confirm_raises(expected_message, username)


class TestNameValidation:

    missing_message = 'name must be provided'
    out_of_range_message = (
        'name must be between {0} and {1} characters long'
        .format(FieldValidator.name_min_length, FieldValidator.name_max_length))
    bad_characters_message = (
        'name must be alphanumeric characters with regular punctuation')
    trailing_spaces_message = 'name must not have trailing spaces'

    def test_good_returns_its_value(self):
        name = 'Fox Mulder'
        assert FieldValidator.validate_name(name) == name

    def test_none_raises(self):
        name = None
        expected_message = self.missing_message
        self.confirm_raises(expected_message, name)

    @staticmethod
    def confirm_raises(expected_message, given_name, field_name='name'):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_name(given_name, field_name)
        assert str(excinfo.value) == expected_message

    def test_too_short_raises(self):
        name = 'a' * (FieldValidator.name_min_length - 1)
        expected_message = self.out_of_range_message
        self.confirm_raises(expected_message, name)

    def test_too_long_raises(self):
        name = 'a' * (FieldValidator.name_max_length + 1)
        expected_message = self.out_of_range_message
        self.confirm_raises(expected_message, name)

    @pytest.mark.parametrize(('name'), (
        ('This $has$ BAD chars'),
        ('This "has" BAD chars'),
        ('This _has_ BAD chars'),
        ('-Has BAD leading char'),
    ))
    def test_bad_characters_raises(self, name):
        expected_message = self.bad_characters_message
        self.confirm_raises(expected_message, name)

    def test_permmited_punctuation_validates(self):
        name = "Mr. BIG-Time, Jr's"
        assert FieldValidator.validate_name(name) == name

    def test_trailing_spaces_raises(self):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_name('trailing spaces  ')
        assert str(excinfo.value) == self.trailing_spaces_message


class TestDescriptionValidation:
    
    missing_message = 'description must be provided'
    out_of_range_message = (
        'description must be between {0} and {1} characters long'
        .format(FieldValidator.description_min_length, FieldValidator.description_max_length))
    leading_spaces_message = 'description must not have leading spaces'
    trailing_spaces_message = 'description must not have trailing spaces'

    def test_good_description_returns_its_value(self):
        description = 'This is a good test.'
        assert FieldValidator.validate_description(description) == description

    def test_description_none_throws(self):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_description(None)
        assert str(excinfo.value) == self.missing_message

    def test_description_too_long_throws(self):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_description('a' * (FieldValidator.description_max_length + 1))
        assert str(excinfo.value) == self.out_of_range_message

    def test_leading_spaces_raises(self):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_description('  leading spaces')
        assert str(excinfo.value) == self.leading_spaces_message

    def test_trailing_spaces_raises(self):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_description('trailing spaces  ')
        assert str(excinfo.value) == self.trailing_spaces_message


class TestTitleValidation:

    missing_message = 'title must be provided'
    out_of_range_message = (
        'title must be between {0} and {1} characters long'
        .format(FieldValidator.title_min_length, FieldValidator.title_max_length))
    bad_lead_message = 'title must begin with an alphanumeric character'
    trailing_spaces_message = 'title must not have trailing spaces'

    def test_good_title_returns_its_value(self):
        title = 'This is a Good Title'
        assert FieldValidator.validate_title(title) == title

    def test_title_none_raises(self):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_title(None)
        assert str(excinfo.value) == self.missing_message

    def test_title_too_long_throws(self):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_title('a' * (FieldValidator.title_max_length + 1))
        assert str(excinfo.value) == self.out_of_range_message

    def test_leading_non_alphanumeric_raises(self):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_title('!bad lead')
        assert str(excinfo.value) == self.bad_lead_message

    def test_trailing_spaces_raises(self):
        with pytest.raises(ValueError) as excinfo:
            FieldValidator.validate_title('trailing spaces  ')
        assert str(excinfo.value) == self.trailing_spaces_message
