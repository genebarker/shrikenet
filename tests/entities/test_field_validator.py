from datetime import datetime, timedelta, timezone

import pytest

from shrike.entities.field_validator import FieldValidator


def confirm_call_raises(function_call, field_name, field_value, expected_message):
    with pytest.raises(ValueError) as excinfo:
        function_call(field_value, field_name)
    assert str(excinfo.value) == expected_message


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
        confirm_call_raises(function_call=FieldValidator.validate_oid,
                       field_name=field_name,
                       field_value=given_oid,
                       expected_message=expected_message)

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
        confirm_call_raises(function_call=FieldValidator.validate_username,
                       field_name=field_name,
                       field_value=given_username,
                       expected_message=expected_message)

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
        confirm_call_raises(function_call=FieldValidator.validate_name,
                       field_name=field_name,
                       field_value=given_name,
                       expected_message=expected_message)

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
        name = 'trailing spaces  '
        expected_message = self.trailing_spaces_message
        self.confirm_raises(expected_message, name)


class TestDescriptionValidation:
    
    missing_message = 'description must be provided'
    out_of_range_message = (
        'description must be between {0} and {1} characters long'
        .format(FieldValidator.description_min_length, FieldValidator.description_max_length))
    leading_spaces_message = 'description must not have leading spaces'
    trailing_spaces_message = 'description must not have trailing spaces'

    def test_good_returns_its_value(self):
        description = 'This is a good test.'
        assert FieldValidator.validate_description(description) == description

    def test_none_raises(self):
        description = None
        expected_message = self.missing_message
        self.confirm_raises(expected_message, description)

    @staticmethod
    def confirm_raises(expected_message, given_description):
        confirm_call_raises(function_call=FieldValidator.validate_description,
                       field_name='description',
                       field_value=given_description,
                       expected_message=expected_message)

    def test_too_long_raises(self):
        description = 'a' * (FieldValidator.description_max_length + 1)
        expected_message = self.out_of_range_message
        self.confirm_raises(expected_message, description)

    def test_leading_spaces_raises(self):
        description = '  leading spaces'
        expected_message = self.leading_spaces_message
        self.confirm_raises(expected_message, description)

    def test_trailing_spaces_raises(self):
        description = 'trailing spaces  '
        expected_message = self.trailing_spaces_message
        self.confirm_raises(expected_message, description)


class TestTitleValidation:

    missing_message = 'title must be provided'
    out_of_range_message = (
        'title must be between {0} and {1} characters long'
        .format(FieldValidator.title_min_length, FieldValidator.title_max_length))
    bad_lead_message = 'title must begin with an alphanumeric character'
    trailing_spaces_message = 'title must not have trailing spaces'

    def test_good_returns_its_value(self):
        title = 'This is a Good Title'
        assert FieldValidator.validate_title(title) == title

    def test_none_raises(self):
        title = None
        expected_message = self.missing_message
        self.confirm_raises(expected_message, title)

    @staticmethod
    def confirm_raises(expected_message, given_title):
        confirm_call_raises(function_call=FieldValidator.validate_title,
                       field_name='title',
                       field_value=given_title,
                       expected_message=expected_message)

    def test_too_long_raises(self):
        title = 'a' * (FieldValidator.title_max_length + 1)
        expected_message = self.out_of_range_message
        self.confirm_raises(expected_message, title)

    def test_leading_non_alphanumeric_raises(self):
        title = '!bad lead'
        expected_message = self.bad_lead_message
        self.confirm_raises(expected_message, title)

    def test_trailing_spaces_raises(self):
        title = 'trailing spaces  '
        expected_message = self.trailing_spaces_message
        self.confirm_raises(expected_message, title)


class TestInstantValidation:

    missing_message = 'instant must be provided'
    bad_value_message = 'instant must be datetime object with timezone'

    GOOD_INSTANT = datetime(2018, 12, 31, 23, 58, tzinfo=timezone.utc)

    def test_good_returns_its_value(self):
        assert FieldValidator.validate_instant(self.GOOD_INSTANT) == self.GOOD_INSTANT

    def test_none_raises(self):
        instant = None
        expected_message = self.missing_message
        self.confirm_raises(expected_message, instant)

    @staticmethod
    def confirm_raises(expected_message, given_instant, field_name='instant'):
        confirm_call_raises(function_call=FieldValidator.validate_instant,
                            field_name=field_name,
                            field_value=given_instant,
                            expected_message=expected_message)

    def test_none_with_alternate_name_raises(self):
        instant = None
        alternate_field_name = 'filing_time'
        expected_message = self.missing_message.replace('instant', alternate_field_name, 1)
        self.confirm_raises(expected_message, instant, alternate_field_name)

    def test_non_datetime_raises(self):
        instant = 'bad datetime'
        expected_message = self.bad_value_message
        self.confirm_raises(expected_message, instant)

    def test_non_datetime_with_alternate_name_raises(self):
        instant = 'bad datetime'
        alternate_field_name = 'timestamp'
        expected_message = self.bad_value_message.replace('instant', alternate_field_name, 1)
        self.confirm_raises(expected_message, instant, field_name=alternate_field_name)

    def test_datetime_without_timezone_raises(self):
        instant = datetime.utcnow()
        expected_message = self.bad_value_message
        self.confirm_raises(expected_message, instant)
