from shrikenet.entities.event import Event
from shrikenet.entities.field_validator import FieldValidator
from shrikenet.entities.record_validator import RecordValidator


class EventValidator(RecordValidator):

    @staticmethod
    def validate_fields(the_object: Event):
        FieldValidator.validate_oid(the_object.oid)
        FieldValidator.validate_instant(the_object.time, 'time')
        FieldValidator.validate_oid(the_object.app_user_oid)
        FieldValidator.validate_tag(the_object.tag)
        FieldValidator.validate_tag(the_object.usecase_tag, 'usecase_tag')
