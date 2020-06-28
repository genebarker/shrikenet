from shrikenet.entities.event import Event
from shrikenet.entities.field_validator import FieldValidator
from shrikenet.entities.record_validator import RecordValidator
from shrikenet.entities.storage_provider import StorageProvider


class EventValidator(RecordValidator):

    text_min_length = 1
    text_max_length = 200

    @staticmethod
    def validate_fields(the_object: Event):
        FieldValidator.validate_oid(the_object.oid)
        FieldValidator.validate_instant(the_object.time, 'time')
        FieldValidator.validate_oid(the_object.app_user_oid)
        FieldValidator.validate_tag(the_object.tag)
        FieldValidator.validate_tag(the_object.usecase_tag, 'usecase_tag')
        FieldValidator.validate_string(the_object.text, 'text',
                                       EventValidator.text_min_length,
                                       EventValidator.text_max_length)

    @staticmethod
    def validate_references(the_object: Event,
                            storage_provider: StorageProvider):
        storage_provider.get_app_user_by_oid(the_object.app_user_oid)
