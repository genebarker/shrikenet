from shrikenet.entities.event import Event
from shrikenet.entities.field_validator import FieldValidator
from shrikenet.entities.record_validator import RecordValidator


class EventValidator(RecordValidator):

    @staticmethod
    def validate_fields(the_object: Event):
        FieldValidator.validate_oid(the_object.oid)
