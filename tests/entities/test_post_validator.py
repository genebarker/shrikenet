import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.entities.post_validator import PostValidator
from shrike.entities.record_validator import RecordValidator

from tests.entities.test_app_user import create_good_app_user
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

    def test_body_can_be_none(self):
        post = create_good_post()
        post.body = None
        assert PostValidator.validate_fields(post) is None

    def test_non_none_empty_body_raises(self):
        post = create_good_post()
        post.body = ''
        self.verify_validation_raises(post)

    def test_body_with_leading_spaces_raises(self):
        post = create_good_post()
        post.body = ' ' + post.body
        self.verify_validation_raises(post)

    def test_body_with_trailing_spaces_raises(self):
        post = create_good_post()
        post.body = post.body + ' '
        self.verify_validation_raises(post)

    def test_body_too_long_raises(self):
        post = create_good_post()
        post.body = 'x' * (PostValidator.MAX_POST_CHARACTERS + 1)
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

    def test_created_time_required(self):
        post = create_good_post()
        post.created_time = None
        self.verify_validation_raises(post)

    def test_created_time_validated(self):
        post = create_good_post()
        post.created_time = 'bad time value'
        self.verify_validation_raises(post)

    def test_created_time_validation_exception_states_correct_field_name(self):
        post = create_good_post()
        post.created_time = 'bad time value'
        with pytest.raises(ValueError) as excinfo:
            PostValidator.validate_fields(post)
        assert str(excinfo.value).startswith('created_time')

class TestReferenceValidation:

    @pytest.fixture
    def storage_provider(self):
        provider = MemoryAdapter()
        provider.open()
        yield provider
        provider.close()

    def test_successful_validation_returns_none(self, storage_provider):
        post = self.create_good_post_with_references(storage_provider)
        assert PostValidator.validate_references(post, storage_provider) is None

    @staticmethod
    def create_good_post_with_references(storage_provider):
        app_user = create_good_app_user()
        storage_provider.add_app_user(app_user)
        post = create_good_post()
        post.author_oid = app_user.oid
        return post

    def test_unknown_author_oid_raises(self, storage_provider):
        post = create_good_post()
        with pytest.raises(KeyError) as excinfo:
            PostValidator.validate_references(post, storage_provider)
        expected_message = 'app_user (oid={}) does not exist'.format(post.author_oid)
        assert expected_message in str(excinfo.value)
