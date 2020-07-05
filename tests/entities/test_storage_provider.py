import pytest

from shrikenet.entities.storage_provider import StorageProvider


class TestStorageProvider:

    def test_interface_cant_be_instantiated(self):
        with pytest.raises(NotImplementedError):
            StorageProvider(None)

    @pytest.fixture
    def storage_provider(self):
        class FakeProvider(StorageProvider):
            def __init__(self, dbonfig=None):
                pass
        return FakeProvider()

    @pytest.mark.parametrize(('method_name', 'args'), (
        ('open', 0),
        ('close', 0),
        ('commit', 0),
        ('rollback', 0),
        ('build_database_schema', 0),
        ('reset_database_objects', 0),
        ('get_version', 0),
        ('get_next_app_user_oid', 0),
        ('get_next_event_oid', 0),
        ('get_next_post_oid', 0),
        ('get_app_user_by_username', 1),
        ('get_app_user_by_oid', 1),
        ('add_app_user', 1),
        ('update_app_user', 1),
        ('get_app_user_count', 0),
        ('exists_app_username', 1),
        ('get_event_by_oid', 1),
        ('add_event', 1),
        ('get_last_event', 0),
        ('get_post_by_oid', 1),
        ('add_post', 1),
        ('update_post', 1),
        ('delete_post_by_oid', 1),
        ('get_post_count', 0),
        ('get_posts', 0),
        ('get_rules', 0),
        ('save_rules', 1),
    ))
    def test_method_is_uncallable(self, storage_provider, method_name, args):
        method = getattr(storage_provider, method_name)
        with pytest.raises(NotImplementedError):
            if args == 0:
                method()
            if args == 1:
                method(None)
            pass
