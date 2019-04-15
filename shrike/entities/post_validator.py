from shrike.entities.field_validator import FieldValidator
from shrike.entities.record_validator import RecordValidator


class PostValidator(RecordValidator):

    MIN_POST_CHARACTERS = 1

    MAX_WORDS = 5000 # About 10 pages of single-spaced 12pt text
    AVG_CHARACTERS_PER_WORD = 4.79
    MAX_POST_CHARACTERS = round(MAX_WORDS * (AVG_CHARACTERS_PER_WORD + 1))

    @staticmethod
    def validate_fields(post):
        FieldValidator.validate_oid(post.oid)
        FieldValidator.validate_title(post.title)
        PostValidator.validate_body(post.body)
        FieldValidator.validate_oid(post.author_oid, 'author_oid')
        FieldValidator.validate_instant(post.created_time, 'created_time')

    @classmethod
    def validate_body(cls, body):
        if body is None: return
        if body == '': raise ValueError('body can not be an empty string')

        FieldValidator.validate_string(
            field_value=body,
            field_name='body',
            min_length=cls.MIN_POST_CHARACTERS,
            max_length=cls.MAX_POST_CHARACTERS,
        )

    @staticmethod
    def validate_references(post, storage_provider):
        storage_provider.get_app_user_by_oid(post.author_oid)
