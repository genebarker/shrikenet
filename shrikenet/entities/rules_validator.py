from shrikenet.entities.field_validator import FieldValidator
from shrikenet.entities.record_validator import RecordValidator


class RulesValidator(RecordValidator):

    @staticmethod
    def validate_fields(rules):
        field_name = "login_fail_threshold_amount"
        lower_limit = 1
        FieldValidator.validate_int(
            rules.login_fail_threshold_count, field_name, lower_limit
        )
        field_name = "login_fail_lock_minutes"
        FieldValidator.validate_int(
            rules.login_fail_lock_minutes, field_name, lower_limit
        )

    @staticmethod
    def validate_references(app_user, storage_provider):
        pass
