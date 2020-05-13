import re
from datetime import datetime


class FieldValidator:
    username_min_length = 4
    username_max_length = 20
    username_regex_pattern = '^[a-zA-Z0-9][a-zA-Z0-9_.]*[a-zA-Z0-9]$'
    name_min_length = 4
    name_max_length = 50
    name_regex_pattern = '^[a-zA-Z0-9][a-zA-Z0-9- .,\']*$'
    description_min_length = 1
    description_max_length = 140
    title_min_length = 1
    title_max_length = 50
    title_regex_pattern = '^[a-zA-Z0-9].*'

    @staticmethod
    def validate_oid(oid, field_name='oid'):
        lower_limit = 1
        return FieldValidator.validate_int(oid, field_name, lower_limit)

    @staticmethod
    def validate_int(value, field_name='value', lower_limit=0):
        if value is None:
            raise ValueError('{} must be provided'.format(field_name))
        if not isinstance(value, int) or value < lower_limit:
            raise ValueError('{0} must be an integer greater than or equal '
                             'to {1}'.format(field_name, lower_limit))
        return value

    @staticmethod
    def validate_username(username, field_name='username'):
        return FieldValidator.validate_string(
            field_value=username,
            field_name=field_name,
            min_length=FieldValidator.username_min_length,
            max_length=FieldValidator.username_max_length,
            regex_pattern=FieldValidator.username_regex_pattern,
            pattern_hint=(field_name + ' must be alphanumeric characters with '
                          'optional underscore and period seperators')
        )

    @staticmethod
    def validate_string(field_value, field_name, min_length, max_length,
                        regex_pattern=None, pattern_hint=None):
        if field_value is None or field_value == '':
            raise ValueError('{} must be provided'.format(field_name))
        if len(field_value) < min_length or len(field_value) > max_length:
            raise ValueError('{0} must be between {1} and {2} characters long'
                             .format(field_name, min_length, max_length))
        if field_value.startswith(' '):
            raise ValueError('{} must not have leading spaces'
                             .format(field_name))
        if field_value.endswith(' '):
            raise ValueError('{} must not have trailing spaces'
                             .format(field_name))
        if regex_pattern is not None:
            regex = re.compile(regex_pattern)
            if not regex.match(field_value):
                raise ValueError(pattern_hint)

        return field_value

    @staticmethod
    def validate_name(name, field_name='name'):
        return FieldValidator.validate_string(
            field_value=name,
            field_name=field_name,
            min_length=FieldValidator.name_min_length,
            max_length=FieldValidator.name_max_length,
            regex_pattern=FieldValidator.name_regex_pattern,
            pattern_hint=(field_name + ' must be alphanumeric characters '
                          'with regular punctuation')
        )

    @staticmethod
    def validate_description(description, field_name='description'):
        return FieldValidator.validate_string(
            field_value=description,
            field_name=field_name,
            min_length=FieldValidator.description_min_length,
            max_length=FieldValidator.description_max_length
        )

    @staticmethod
    def validate_title(title, field_name='title'):
        return FieldValidator.validate_string(
            field_value=title,
            field_name=field_name,
            min_length=FieldValidator.title_min_length,
            max_length=FieldValidator.title_max_length,
            regex_pattern=FieldValidator.title_regex_pattern,
            pattern_hint=('{} must begin with an alphanumeric character'
                          .format(field_name)),
        )

    @staticmethod
    def validate_instant(instant, field_name='instant'):
        if instant is None:
            raise ValueError('{} must be provided'.format(field_name))
        if not isinstance(instant, datetime) or instant.tzinfo is None:
            raise ValueError('{} must be datetime object with timezone'
                             .format(field_name))
        return instant
