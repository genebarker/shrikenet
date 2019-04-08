import pytest

from shrike.entities.post_validator import PostValidator
from shrike.entities.record_validator import RecordValidator

from tests.entities.test_post import create_good_post


class TestGeneralProperties:

    def test_is_a_record_validator(self):
        assert issubclass(PostValidator, RecordValidator)


class TestFieldValidation:

    def test_successful_validation_returns_none(self):
        post = create_good_post()
        assert PostValidator.validate_fields(post) is None

    def test_oid_required(self):
        post = create_good_post()
        post.oid = None
        self.verify_validation_raises(post)

    @staticmethod
    def verify_validation_raises(post):
        with pytest.raises(ValueError):
            PostValidator.validate_fields(post)

    def test_oid_validated(self):
        post = create_good_post()
        post.oid = 'bad oid'
        self.verify_validation_raises(post)

    def test_title_required(self):
        post = create_good_post()
        post.title = None
        self.verify_validation_raises(post)

    def test_title_validated(self):
        post = create_good_post()
        post.title = '! bad title'
        self.verify_validation_raises(post)

    def test_author_oid_required(self):
        post = create_good_post()
        post.author_oid = None
        self.verify_validation_raises(post)

    def test_author_oid_validated(self):
        post = create_good_post()
        post.author_oid = 'bad author oid'
        self.verify_validation_raises(post)

    def test_author_oid_validation_exception_states_correct_field_name(self):
        post = create_good_post()
        post.author_oid = 'bad author oid'
        with pytest.raises(ValueError) as excinfo:
            PostValidator.validate_fields(post)
        assert str(excinfo.value).startswith('author_oid')
        