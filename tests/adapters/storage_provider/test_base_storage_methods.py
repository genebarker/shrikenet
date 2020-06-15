import pytest

from tests.adapters.storage_provider.test_app_user import create_user


@pytest.mark.parametrize(
    'create_method, get_method_name',
    [
        (create_user, 'get_app_user_by_oid'),
    ],
)
def test_get_object_by_oid_gets_record(db, create_method, get_method_name):
    obj = create_method(db)
    get_obj_by_oid = getattr(db, get_method_name)
    stored_obj = get_obj_by_oid(obj.oid)
    assert stored_obj == obj


@pytest.mark.parametrize(
    'create_method, an_attr_name, get_method_name',
    [
        (create_user, 'name', 'get_app_user_by_oid'),
    ],
)
def test_get_object_by_oid_returns_a_copy(db, create_method,
                                          an_attr_name, get_method_name):
    obj = create_method(db)
    get_obj_by_oid = getattr(db, get_method_name)
    copied_obj = get_obj_by_oid(obj.oid)
    setattr(copied_obj, an_attr_name, 'Different')
    stored_obj = get_obj_by_oid(obj.oid)
    assert stored_obj != copied_obj
