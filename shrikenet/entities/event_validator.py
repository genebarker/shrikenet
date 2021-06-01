from shrikenet.entities.event import LogEntry
from shrikenet.entities.field_validator import FieldValidator
from shrikenet.entities.record_validator import RecordValidator
from shrikenet.entities.storage_provider import StorageProvider


class EventValidator(RecordValidator):

    text_min_length = 1
    text_max_length = 200

    @staticmethod
    def validate_fields(the_object: LogEntry):
        event = the_object
        FieldValidator.validate_oid(event.oid)
        FieldValidator.validate_instant(event.time, 'time')
        FieldValidator.validate_oid(event.app_user_oid)
        FieldValidator.validate_tag(event.tag)
        FieldValidator.validate_tag(event.usecase_tag, 'usecase_tag')
        FieldValidator.validate_string(event.text, 'text',
                                       EventValidator.text_min_length,
                                       EventValidator.text_max_length)

    @staticmethod
    def validate_references(the_object: LogEntry,
                            storage_provider: StorageProvider):
        event = the_object
        storage_provider.get_app_user_by_oid(event.app_user_oid)
