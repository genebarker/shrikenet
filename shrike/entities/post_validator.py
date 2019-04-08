from shrike.entities.field_validator import FieldValidator
from shrike.entities.record_validator import RecordValidator


class PostValidator(RecordValidator):

    @staticmethod
    def validate_fields(post):
        FieldValidator.validate_oid(post.oid)
        FieldValidator.validate_title(post.title)
        FieldValidator.validate_oid(post.author_oid, 'author_oid')
        FieldValidator.validate_instant(post.created_time, 'created_time')
