def test_schema_exists_after_build(db):
    db.build_database_schema()
    assert_database_in_initial_state(db)


def assert_database_in_initial_state(db):
    app_user_count = select_value(db, "SELECT count(*) FROM app_user")
    assert app_user_count == 0
    log_entry_count = select_value(db, "SELECT count(*) FROM log_entry")
    assert log_entry_count == 0
    post_count = select_value(db, "SELECT count(*) FROM post")
    assert post_count == 0
    rule_count = select_value(db, "SELECT count(*) FROM rule")
    assert rule_count == 2


def select_value(db, sql):
    parms = []
    value = db._select_value(sql, parms)
    return value


def test_database_objects_reset_to_initial_state(db):
    db.reset_database_objects()
    assert_database_in_initial_state(db)
