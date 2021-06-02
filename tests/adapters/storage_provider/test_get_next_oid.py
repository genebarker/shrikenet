import pytest


GET_NEXT_OID_METHODS = [
    'get_next_app_user_oid',
    'get_next_log_entry_oid',
    'get_next_post_oid',
]


@pytest.mark.parametrize('method_name,', GET_NEXT_OID_METHODS)
def test_get_next_oid_positive(db, method_name):
    get_next_oid = getattr(db, method_name)
    assert get_next_oid() > 0


@pytest.mark.parametrize('method_name,', GET_NEXT_OID_METHODS)
def test_get_next_oid_increments(db, method_name):
    get_next_oid = getattr(db, method_name)
    oid1 = get_next_oid()
    oid2 = get_next_oid()
    assert oid2 == oid1 + 1


@pytest.mark.parametrize('method_name,', GET_NEXT_OID_METHODS)
def test_get_next_oid_doesnt_rollback(db, method_name):
    get_next_oid = getattr(db, method_name)
    db.commit()
    oid1 = get_next_oid()
    db.rollback()
    oid2 = get_next_oid()
    assert oid2 > oid1
