from shrikenet.entities.log_entry import LogEntry
from shrikenet.entities.field_validator import FieldValidator
from shrikenet.entities.record_validator import RecordValidator
from shrikenet.entities.storage_provider import StorageProvider


class LogEntryValidator(RecordValidator):

    text_min_length = 1
    text_max_length = 200

    @staticmethod
    def validate_fields(the_object: LogEntry):
        log_entry = the_object
        FieldValidator.validate_oid(log_entry.oid)
        FieldValidator.validate_instant(log_entry.time, "time")
        FieldValidator.validate_oid(log_entry.app_user_oid)
        FieldValidator.validate_tag(log_entry.tag)
        FieldValidator.validate_tag(log_entry.usecase_tag, "usecase_tag")
        FieldValidator.validate_string(
            log_entry.text,
            "text",
            LogEntryValidator.text_min_length,
            LogEntryValidator.text_max_length,
        )

    @staticmethod
    def validate_references(
        the_object: LogEntry, storage_provider: StorageProvider
    ):
        log_entry = the_object
        storage_provider.get_app_user_by_oid(log_entry.app_user_oid)
