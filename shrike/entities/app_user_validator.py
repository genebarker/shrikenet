from shrike.entities.field_validator import FieldValidator
from shrike.entities.record_validator import RecordValidator


class AppUserValidator(RecordValidator):

    @staticmethod
    def validate_fields(app_user):
        FieldValidator.validate_oid(app_user.oid)
        FieldValidator.validate_username(app_user.username)
        FieldValidator.validate_name(app_user.name)
