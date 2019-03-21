from .field_validator import FieldValidator
from .record_validator import RecordValidator


class AppUserValidator(RecordValidator):

    @staticmethod
    def validate_fields(app_user):
        FieldValidator.validate_id(app_user.id)
        FieldValidator.validate_username(app_user.username)
        FieldValidator.validate_name(app_user.name)
